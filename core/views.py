from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import StreamingHttpResponse, FileResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm
from .drive_audio import build_drive_audio_url, extract_drive_file_id
from .models import StudentProfile, Lesson, ListeningQuestion, HomeBackground, SecurityAlert, Part2Topic, Part2Voice, ListeningPartMaterial, ListeningPartQuestion
from .supabase_storage import create_signed_url


def get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def home(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    home_background = HomeBackground.objects.filter(is_active=True).order_by("-created_at").first()

    return render(request, "core/home.html", {
        "login_form": login_form,
        "register_form": register_form,
        "home_background": home_background,
    })


def register_view(request):
    if request.method != "POST":
        return redirect("home")

    form = RegisterForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Thông tin đăng ký chưa hợp lệ.")
        return redirect("home")

    full_name = form.cleaned_data["full_name"]
    phone = form.cleaned_data["phone"]
    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]

    if User.objects.filter(username=email).exists():
        messages.error(request, "Email này đã được đăng ký.")
        return redirect("home")

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=full_name,
        is_active=False
    )

    StudentProfile.objects.create(
        user=user,
        full_name=full_name,
        phone=phone,
        email=email,
        status="pending"
    )

    messages.success(request, "Đăng ký thành công. Vui lòng chờ admin duyệt tài khoản.")
    return redirect("home")


def login_view(request):
    if request.method != "POST":
        return redirect("home")

    ip = get_client_ip(request) or "unknown"
    throttle_key = f"login_fail:{ip}"
    fail_count = cache.get(throttle_key, 0)

    if fail_count >= 5:
        messages.error(request, "Bạn đăng nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút.")
        return redirect("home")

    form = LoginForm(request.POST)

    if not form.is_valid():
        cache.set(throttle_key, fail_count + 1, 60 * 15)
        messages.error(request, "Thông tin đăng nhập chưa hợp lệ.")
        return redirect("home")

    account = form.cleaned_data["email"].strip()
    password = form.cleaned_data["password"]

    candidates = [account]
    if account.lower() == "admin":
        candidates = ["admin", "admin@gmail.com"]

    user_check = User.objects.filter(username__in=candidates).first()

    if user_check and not user_check.is_active:
        messages.error(request, "Tài khoản của bạn đang chờ admin duyệt.")
        return redirect("home")

    user = None
    for username in candidates:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            break

    if user is None:
        cache.set(throttle_key, fail_count + 1, 60 * 15)

        target_user = User.objects.filter(username__in=candidates).first()

        if target_user:
            SecurityAlert.objects.get_or_create(
                user=target_user,
                reason="Có nhiều lần đăng nhập sai mật khẩu",
                defaults={
                    "ip_address": ip
                }
            )

        messages.error(request, "Tài khoản hoặc mật khẩu không đúng.")
        return redirect("home")

    cache.delete(throttle_key)
    login(request, user)
    return redirect("dashboard")




def _google_drive_download_response(file_id):
    session = requests.Session()

    base_url = "https://drive.google.com/uc"
    params = {
        "export": "download",
        "id": file_id,
    }

    response = session.get(base_url, params=params, stream=True, timeout=30)

    # Google Drive đôi khi yêu cầu confirm token cho file lớn hoặc bị quét virus.
    token = None

    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break

    if token:
        params["confirm"] = token
        response = session.get(base_url, params=params, stream=True, timeout=30)

    content_type = response.headers.get("Content-Type", "")

    if response.status_code != 200:
        raise Http404("Không tải được audio từ Google Drive.")

    # Nếu Google trả về HTML thì link Drive chưa public hoặc bị chặn tải trực tiếp.
    if "text/html" in content_type.lower():
        raise Http404("Google Drive chưa trả về file MP3 trực tiếp. Hãy bật chia sẻ file: Bất kỳ ai có đường liên kết ở quyền Người xem.")

    django_response = StreamingHttpResponse(
        response.iter_content(chunk_size=8192),
        content_type=content_type or "audio/mpeg",
    )

    total_size = response.headers.get("Content-Length")

    if total_size:
        django_response["Content-Length"] = total_size

    django_response["Accept-Ranges"] = "bytes"
    django_response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    django_response["Pragma"] = "no-cache"
    django_response["Expires"] = "0"
    django_response["X-Content-Type-Options"] = "nosniff"
    django_response["Content-Disposition"] = 'inline; filename="tsa-audio.mp3"'

    return django_response


@login_required
def dashboard(request):
    lessons = Lesson.objects.all().order_by("-created_at")

    is_admin_user = (
        request.user.is_staff
        or request.user.is_superuser
        or request.user.username == "admin"
        or request.user.email == "admin@gmail.com"
    )

    if is_admin_user:
        return render(request, "core/dashboard.html", {
            "lessons": lessons
        })

    return redirect("listening")

    return redirect("listening")



@login_required
def listening_view(request):
    try:
        part = int(request.GET.get("part", 1))
    except ValueError:
        part = 1

    if part not in [1, 2, 3, 4]:
        part = 1

    questions = ListeningQuestion.objects.filter(part=part).order_by("question_number")
    parts = [1, 2, 3, 4]

    response = render(request, "core/listening.html", {
        "part": part,
        "parts": parts,
        "questions": questions,
        "total_questions": questions.count(),
    })

    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response


@login_required
def secure_audio_view(request, question_id):
    question = get_object_or_404(ListeningQuestion, id=question_id)

    drive_file_id = getattr(question, "audio_drive_file_id", "") or extract_drive_file_id(getattr(question, "audio_drive_link", ""))

    if drive_file_id:
        return _google_drive_download_response(drive_file_id)

    if getattr(question, "audio_file", None):
        response = FileResponse(question.audio_file.open("rb"), content_type="audio/mpeg")
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        response["Content-Disposition"] = 'inline; filename="tsa-audio.mp3"'
        return response

    if getattr(question, "audio_url", ""):
        response = HttpResponseRedirect(question.audio_url)
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        return response

    raise Http404("Audio không tồn tại.")

@login_required
@require_POST
def security_event_view(request):
    event_type = request.POST.get("event_type", "unknown")[:120]
    severity = request.POST.get("severity", "medium")[:20]

    if severity not in ["low", "medium", "high", "critical"]:
        severity = "medium"

    reason_map = {
        "print_attempt": "Học viên cố gắng in hoặc lưu PDF",
        "save_attempt": "Học viên cố gắng lưu trang",
        "source_attempt": "Học viên cố gắng xem mã nguồn trang",
        "devtools_attempt": "Học viên có dấu hiệu mở công cụ kiểm tra trang",
        "tab_blur": "Học viên rời khỏi tab làm bài",
        "screenshot_key": "Học viên bấm phím Print Screen",
    }

    reason = reason_map.get(event_type, f"Sự kiện bảo mật: {event_type}")

    SecurityAlert.objects.create(
        user=request.user,
        severity=severity,
        reason=reason,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
    )

    return JsonResponse({"ok": True})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def admin_listening_parts(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.username == "admin"):
        return redirect("listening")

    part_counts = {
        1: ListeningQuestion.objects.filter(part=1).count(),
        2: ListeningQuestion.objects.filter(part=2).count(),
        3: ListeningQuestion.objects.filter(part=3).count(),
        4: ListeningQuestion.objects.filter(part=4).count(),
    }

    return render(request, "core/admin_listening_parts.html", {
        "part_counts": part_counts,
    })


@login_required
def admin_part1_questions(request):
    if not (request.user.is_staff or request.user.is_superuser or request.user.username == "admin"):
        return redirect("listening")

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "create_blank":
            try:
                count = int(request.POST.get("create_count", 13))
            except ValueError:
                count = 13

            count = max(1, min(count, 100))

            current_max = 0
            for q in ListeningQuestion.objects.filter(part=1):
                try:
                    current_max = max(current_max, int(q.question_number or 0))
                except Exception:
                    pass

            for i in range(1, count + 1):
                ListeningQuestion.objects.create(
                    part=1,
                    question_number=current_max + i,
                    question_text=f"Câu hỏi {current_max + i}",
                    option_a="",
                    option_b="",
                    option_c="",
                    correct_answer="A",
                    listening_transcript="",
                )

            messages.success(request, f"Đã tạo thêm {count} dòng Part 1.")
            return redirect("admin_part1_questions")

        if action == "save_all":
            row_ids = request.POST.getlist("row_id")

            for row_id in row_ids:
                q = ListeningQuestion.objects.filter(id=row_id, part=1).first()
                if not q:
                    continue

                try:
                    q.question_number = int(request.POST.get(f"question_number_{row_id}") or q.question_number or 1)
                except ValueError:
                    pass

                q.question_text = request.POST.get(f"question_text_{row_id}", "").strip()
                q.option_a = request.POST.get(f"option_a_{row_id}", "").strip()
                q.option_b = request.POST.get(f"option_b_{row_id}", "").strip()
                q.option_c = request.POST.get(f"option_c_{row_id}", "").strip()
                posted_correct = request.POST.get(f"correct_answer_{row_id}")
                if posted_correct is not None:
                    q.correct_answer = posted_correct.strip().upper()[:1] or q.correct_answer or "A"
                q.listening_transcript = request.POST.get(f"listening_transcript_{row_id}", "").strip()

                if hasattr(q, "audio_drive_link"):
                    q.audio_drive_link = request.POST.get(f"audio_drive_link_{row_id}", "").strip()

                audio_url_key = f"audio_url_{row_id}"
                if hasattr(q, "audio_url") and audio_url_key in request.POST:
                    q.audio_url = request.POST.get(audio_url_key, "").strip()

                q.save()

            messages.success(request, "Đã cập nhật hàng loạt câu hỏi Part 1.")
            return redirect("admin_part1_questions")

        if action == "delete_selected":
            selected_ids = request.POST.getlist("selected_id")
            deleted_count, _ = ListeningQuestion.objects.filter(id__in=selected_ids, part=1).delete()
            messages.success(request, f"Đã xóa {deleted_count} câu hỏi Part 1 đã chọn.")
            return redirect("admin_part1_questions")

        if action == "delete_one":
            delete_id = request.POST.get("delete_id")
            ListeningQuestion.objects.filter(id=delete_id, part=1).delete()
            messages.success(request, "Đã xóa 1 câu hỏi Part 1.")
            return redirect("admin_part1_questions")

    questions = ListeningQuestion.objects.filter(part=1).order_by("question_number", "id")

    return render(request, "core/admin_part1_questions.html", {
        "questions": questions,
        "total_questions": questions.count(),
    })




# ===== Custom admin student lookup/profile page =====
def _is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@csrf_exempt
@user_passes_test(_is_admin_user)
def admin_student_lookup(request):
    q = (request.GET.get("q") or request.POST.get("q") or "").strip()
    profile_id = (request.GET.get("profile_id") or request.POST.get("profile_id") or "").strip()

    results = StudentProfile.objects.none()
    selected = None

    if q:
        filters = (
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(student_id__icontains=q)
        )

        if q.isdigit():
            filters |= Q(id=int(q)) | Q(user__id=int(q))

        results = StudentProfile.objects.filter(filters).select_related("user").distinct().order_by("-id")[:20]

    if profile_id:
        selected = StudentProfile.objects.filter(id=profile_id).select_related("user").first()
    elif results:
        selected = results.first()

    if request.method == "POST" and request.POST.get("action") == "save_profile":
        selected = StudentProfile.objects.filter(id=request.POST.get("profile_id")).select_related("user").first()

        if not selected:
            messages.error(request, "Chưa chọn học viên để lưu.")
            return redirect("admin_student_lookup")

        gmail = request.POST.get("gmail", "").strip()
        phone = request.POST.get("phone", "").strip()
        full_name = request.POST.get("full_name", "").strip()
        student_id = request.POST.get("student_id", "").strip()

        selected.email = gmail
        selected.phone = phone
        selected.full_name = full_name
        selected.student_id = student_id
        selected.save()

        if selected.user:
            selected.user.email = gmail
            selected.user.first_name = full_name
            selected.user.save()

        messages.success(request, "Đã lưu hồ sơ học viên.")
        return redirect(f"{request.path}?profile_id={selected.id}&q={gmail or phone or full_name or student_id or q}")

    if request.method == "POST" and request.POST.get("action") == "delete_profile":
        target = StudentProfile.objects.filter(id=request.POST.get("profile_id")).select_related("user").first()

        if target:
            target.email = ""
            target.phone = ""
            target.full_name = ""
            target.student_id = ""
            target.save()

            if target.user:
                target.user.email = ""
                target.user.first_name = ""
                target.user.last_name = ""
                target.user.save()

            messages.success(request, "Đã xóa thông tin hồ sơ học viên.")

        return redirect("admin_student_lookup")

    saved_profiles = StudentProfile.objects.select_related("user").all().order_by("-id")

    return render(request, "core/admin_student_lookup.html", {
        "q": q,
        "results": results,
        "selected": selected,
        "saved_profiles": saved_profiles,
        "student_id_value": selected.student_id if selected else "",
        "phone_value": selected.phone if selected else "",
        "profile_email_value": selected.email if selected else "",
        "profile_name_value": selected.full_name if selected else "",
    })
# ===== End custom admin student lookup/profile page =====








# ===== Admin management placeholder for Listening Part 2 =====
def admin_part2_questions(request):
    return render(request, "core/admin_part_placeholder.html", {
        "part_number": 2,
        "part_title": "Part 2",
        "part_desc": "Part 2 sẽ là khu vực quản lý topic, 4 voice, pool đáp án A-B-C-D, đáp án đúng và transcript. Hiện chưa nhập dữ liệu thật.",
    })

def _legacy_admin_part3_questions_placeholder(request):
    return render(request, "core/admin_part_placeholder.html", {
        "part_number": 3,
        "part_title": "Part 3",
        "part_desc": "Part 3 đã mở khu vực quản lý dữ liệu. Hiện chưa có dữ liệu thật, sẽ thiết kế chi tiết sau.",
    })

def _legacy_admin_part4_questions_placeholder(request):
    return render(request, "core/admin_part_placeholder.html", {
        "part_number": 4,
        "part_title": "Part 4",
        "part_desc": "Part 4 đã mở khu vực quản lý dữ liệu. Hiện chưa có dữ liệu thật, sẽ thiết kế chi tiết sau.",
    })
# ===== End admin management placeholder for Listening Part 2 =====


# ===== Student listening interfaces =====
def student_part2_page(request):
    return render(request, "core/listening_part2.html")

def _legacy_student_part3_page_placeholder(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 3,
        "part_title": "Part 3",
        "part_desc": "Giao diện học viên Part 3 hiện chưa có dữ liệu.",
    })

def _legacy_student_part4_page_placeholder(request):
    return render(request, "core/listening_part_placeholder.html", {
        "part_number": 4,
        "part_title": "Part 4",
        "part_desc": "Giao diện học viên Part 4 hiện chưa có dữ liệu.",
    })
# ===== End student listening interfaces =====


# ===== Custom Admin Part 2 management =====
def _is_admin_user_part2(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(_is_admin_user_part2)
def admin_part2_questions(request):
    topics = Part2Topic.objects.all().order_by("-id")

    if request.method == "POST" and request.POST.get("action") == "create_topic":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        if not title:
            messages.error(request, "Bạn cần nhập tên chủ đề.")
            return redirect("admin_part2_questions")

        topic = Part2Topic.objects.create(title=title, description=description)

        # Tạo sẵn 4 voice cho 4 người
        for i in range(1, 5):
            Part2Voice.objects.create(topic=topic, order=i)

        messages.success(request, "Đã tạo chủ đề Part 2.")
        return redirect("admin_part2_topic_detail", topic_id=topic.id)

    return render(request, "core/admin_part2_topics.html", {
        "topics": topics,
    })


@user_passes_test(_is_admin_user_part2)
def admin_part2_topic_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id)

    # Luôn đảm bảo có 4 voice chính
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(topic=topic, order=i)

    voices = list(topic.voices.all().order_by("order", "id"))

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.voice_info = request.POST.get("voice_info", "").strip()
        topic.save()

        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.audio_url = request.POST.get(prefix + "audio_url", "").strip()
            voice.answer_a = request.POST.get(prefix + "answer_a", "").strip()
            voice.answer_b = request.POST.get(prefix + "answer_b", "").strip()
            voice.answer_c = request.POST.get(prefix + "answer_c", "").strip()
            voice.answer_d = request.POST.get(prefix + "answer_d", "").strip()
            voice.transcript = request.POST.get(prefix + "transcript", "").strip()
            voice.correct_answer = request.POST.get(prefix + "correct_answer", "").strip()
            voice.save()

        messages.success(request, "Đã lưu dữ liệu chủ đề Part 2.")
        return redirect("admin_part2_topic_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "delete_topic":
        topic.delete()
        messages.success(request, "Đã xóa chủ đề Part 2.")
        return redirect("admin_part2_questions")

    return render(request, "core/admin_part2_topic_detail.html", {
        "topic": topic,
        "voices": voices,
    })
# ===== End Custom Admin Part 2 management =====


# ===== Part 2 May Gioi final admin/student layout =====
PART2_GIOI_TOPICS = [
    "Topic Protect the environment",
    "Topic Protect the environment 2",
    "Topic Online shopping",
    "Topic Listening to music",
    "Topic Outdoor activities",
    "Topic The place to run",
    "Topic Do exercise",
    "Topic The internet",
    "Topic The Art",
    "Topic Travel to work.",
    "Topic Studying.",
    "Topic Studying phiên bản 2.",
]


def _is_admin_user_part2_gioi(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _seed_part2_gioi_topics():
    for title in PART2_GIOI_TOPICS:
        topic, created = Part2Topic.objects.get_or_create(
            version="gioi",
            title=title,
            defaults={"description": "Chủ đề Mày giỏi"}
        )

        existing_orders = set(topic.voices.values_list("order", flat=True))
        for i in range(1, 5):
            if i not in existing_orders:
                Part2Voice.objects.create(
                    topic=topic,
                    order=i,
                    question_text=f"Câu hỏi {i}"
                )


def _ensure_four_gioi_rows(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Câu hỏi {i}"
            )


@user_passes_test(_is_admin_user_part2_gioi)
def admin_part2_gioi_topics(request):
    _seed_part2_gioi_topics()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")

    return render(request, "core/admin_part2_gioi_topics.html", {
        "topics": topics,
    })


@csrf_exempt
@user_passes_test(_is_admin_user_part2_gioi)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_four_gioi_rows(topic)

    voices = list(topic.voices.all().order_by("order", "id"))

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.save()

        for voice in voices:
            prefix = f"voice_{voice.id}_"

            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = f"Person {voice.order}"
            voice.data_choices = request.POST.get(prefix + "data_choices", "").strip()
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()

            # Mày giỏi dùng 1 audio chung theo topic
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu dữ liệu chủ đề Mày giỏi.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "delete_topic":
        topic.delete()
        messages.success(request, "Đã xóa chủ đề Mày giỏi.")
        return redirect("admin_part2_gioi_topics")

    rows = []
    for voice in voices:
        options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voices = list(topic.voices.all().order_by("order", "id"))

    rows = []
    for voice in voices:
        options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
    })
# ===== End Part 2 May Gioi final admin/student layout =====


# ===== Part 2 May Gioi ONE VOICE final =====
PART2_GIOI_TOPICS = [
    "Topic Protect the environment",
    "Topic Protect the environment 2",
    "Topic Online shopping",
    "Topic Listening to music",
    "Topic Outdoor activities",
    "Topic The place to run",
    "Topic Do exercise",
    "Topic The internet",
    "Topic The Art",
    "Topic Travel to work.",
    "Topic Studying.",
    "Topic Studying phiên bản 2.",
]


def _is_admin_user_part2_gioi_one(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _seed_part2_gioi_topics_one_voice():
    for title in PART2_GIOI_TOPICS:
        topic, created = Part2Topic.objects.get_or_create(
            version="gioi",
            title=title,
            defaults={"description": "Chủ đề Mày giỏi"}
        )

        # Mày giỏi chỉ giữ 1 voice tổng
        topic.voices.exclude(order=1).delete()

        voice, created_voice = Part2Voice.objects.get_or_create(
            topic=topic,
            order=1,
            defaults={"question_text": "Câu hỏi tổng"}
        )

        if not voice.question_text:
            voice.question_text = "Câu hỏi tổng"
            voice.save()


def _get_gioi_total_voice(topic):
    topic.voices.exclude(order=1).delete()
    voice, created = Part2Voice.objects.get_or_create(
        topic=topic,
        order=1,
        defaults={"question_text": "Câu hỏi tổng"}
    )
    return voice


@user_passes_test(_is_admin_user_part2_gioi_one)
def admin_part2_gioi_topics(request):
    _seed_part2_gioi_topics_one_voice()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")

    return render(request, "core/admin_part2_gioi_topics.html", {
        "topics": topics,
    })


@csrf_exempt
@user_passes_test(_is_admin_user_part2_gioi_one)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voice = _get_gioi_total_voice(topic)

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.save()

        voice.is_locked = request.POST.get("voice_is_locked") == "on"
        voice.order = int(request.POST.get("voice_order", 1) or 1)
        voice.question_text = f"Person {voice.order}"
        voice.data_choices = request.POST.get("data_choices", "").strip()
        voice.correct_data = request.POST.get("correct_data", "").strip()
        voice.audio_url = topic.audio_url
        voice.save()

        messages.success(request, "Đã lưu dữ liệu chủ đề Mày giỏi.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "voice": voice,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voice = _get_gioi_total_voice(topic)
    options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "voice": voice,
        "options": options,
    })
# ===== End Part 2 May Gioi ONE VOICE final =====


# ===== Part 2 final clean: admin gioi one audio, student choose version =====
PART2_GIOI_TOPICS = [
    "Topic Protect the environment",
    "Topic Protect the environment 2",
    "Topic Online shopping",
    "Topic Listening to music",
    "Topic Outdoor activities",
    "Topic The place to run",
    "Topic Do exercise",
    "Topic The internet",
    "Topic The Art",
    "Topic Travel to work.",
    "Topic Studying.",
    "Topic Studying phiên bản 2.",
]


def _is_admin_user_part2_final(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _seed_part2_gioi_topics_final():
    for title in PART2_GIOI_TOPICS:
        topic, _ = Part2Topic.objects.get_or_create(
            version="gioi",
            title=title,
            defaults={"description": "Chủ đề Mày giỏi"}
        )

        # Mày giỏi chỉ được có 1 voice tổng
        topic.voices.exclude(order=1).delete()

        voice, _ = Part2Voice.objects.get_or_create(
            topic=topic,
            order=1,
            defaults={"question_text": "Câu hỏi tổng"}
        )

        if not voice.question_text:
            voice.question_text = "Câu hỏi tổng"
            voice.save()


def _get_part2_gioi_total_voice(topic):
    topic.voices.exclude(order=1).delete()
    voice, _ = Part2Voice.objects.get_or_create(
        topic=topic,
        order=1,
        defaults={"question_text": "Câu hỏi tổng"}
    )
    return voice


@user_passes_test(_is_admin_user_part2_final)
def admin_part2_gioi_topics(request):
    _seed_part2_gioi_topics_final()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")
    return render(request, "core/admin_part2_gioi_topics.html", {"topics": topics})


@csrf_exempt
@user_passes_test(_is_admin_user_part2_final)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voice = _get_part2_gioi_total_voice(topic)

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.save()

        voice.is_locked = request.POST.get("voice_is_locked") == "on"
        voice.order = 1
        voice.question_text = f"Person {voice.order}"
        voice.data_choices = request.POST.get("data_choices", "").strip()
        voice.correct_data = request.POST.get("correct_data", "").strip()
        voice.audio_url = topic.audio_url
        voice.save()

        messages.success(request, "Đã lưu dữ liệu Mày giỏi.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "voice": voice,
        "options": options,
    })


def student_part2_page(request):
    return render(request, "core/student_part2_choose_version.html")


def student_part2_gioi_topics(request):
    _seed_part2_gioi_topics_final()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày giỏi",
        "topics": topics,
        "back_url": "/listening/part-4/",
        "topic_url_prefix": "/listening/part-4/may-gioi/",
    })


def student_part2_dot_topics(request):
    topics = Part2Topic.objects.filter(version="kem").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày dốt",
        "topics": topics,
        "back_url": "/listening/part-4/",
        "topic_url_prefix": "/listening/part-4/may-dot/",
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    voice = _get_part2_gioi_total_voice(topic)
    options = [x.strip() for x in (voice.data_choices or "").splitlines() if x.strip()]
    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "voice": voice,
        "options": options,
    })


def student_part2_dot_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="kem")
    voices = list(topic.voices.all().order_by("order", "id"))
    return render(request, "core/listening_part2.html", {
        "topic": topic,
        "voices": voices,
    })
# ===== End Part 2 final clean =====


# ===== Part 2 choose version for admin and student =====
def _is_admin_user_part2_choose(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(_is_admin_user_part2_choose)
def admin_part2_questions(request):
    gioi_count = Part2Topic.objects.filter(version="gioi").count() if hasattr(Part2Topic, "version") else 0
    kem_count = Part2Topic.objects.filter(version="kem").count() if hasattr(Part2Topic, "version") else 0

    return render(request, "core/admin_part2_choose_version.html", {
        "gioi_count": gioi_count,
        "kem_count": kem_count,
    })


def student_part2_page(request):
    gioi_count = Part2Topic.objects.filter(version="gioi").count() if hasattr(Part2Topic, "version") else 0
    kem_count = Part2Topic.objects.filter(version="kem").count() if hasattr(Part2Topic, "version") else 0

    return render(request, "core/student_part2_choose_version.html", {
        "gioi_count": gioi_count,
        "kem_count": kem_count,
    })
# ===== End Part 2 choose version for admin and student =====


# ===== Part 2 May Gioi final: 1 audio + 4 person questions =====
PART2_GIOI_TOPICS = [
    "Topic Protect the environment",
    "Topic Protect the environment 2",
    "Topic Online shopping",
    "Topic Listening to music",
    "Topic Outdoor activities",
    "Topic The place to run",
    "Topic Do exercise",
    "Topic The internet",
    "Topic The Art",
    "Topic Travel to work.",
    "Topic Studying.",
    "Topic Studying phiên bản 2.",
]


def _is_admin_user_part2_gioi_4p(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _seed_part2_gioi_topics_4p():
    for title in PART2_GIOI_TOPICS:
        topic, _ = Part2Topic.objects.get_or_create(
            version="gioi",
            title=title,
            defaults={"description": "Chủ đề Mày giỏi"}
        )

        existing_orders = set(topic.voices.values_list("order", flat=True))
        for i in range(1, 5):
            if i not in existing_orders:
                Part2Voice.objects.create(
                    topic=topic,
                    order=i,
                    question_text=f"Person {i}"
                )

        # Mày giỏi chỉ giữ đúng 4 person
        topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()


def _ensure_gioi_four_persons(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Person {i}"
            )

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()


@user_passes_test(_is_admin_user_part2_gioi_4p)
def admin_part2_gioi_topics(request):
    _seed_part2_gioi_topics_4p()
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")

    return render(request, "core/admin_part2_gioi_topics.html", {
        "topics": topics,
    })


@csrf_exempt
@user_passes_test(_is_admin_user_part2_gioi_4p)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_persons(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.voice_info = request.POST.get("voice_info", "").strip()
        topic.save()

        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = f"Person {voice.order}"
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu dữ liệu Mày giỏi.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_persons(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== End Part 2 May Gioi final: 1 audio + 4 person questions =====


# ===== Fix student Part 2 topic list routes =====
def student_part2_gioi_topics(request):
    topics = Part2Topic.objects.filter(version="gioi").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày giỏi",
        "topics": topics,
        "back_url": "/listening/part-4/",
        "topic_url_prefix": "/listening/part-4/may-gioi/",
    })


def student_part2_kem_topics(request):
    topics = Part2Topic.objects.filter(version="kem").order_by("id")
    return render(request, "core/student_part2_topic_list.html", {
        "version_title": "Mày kém",
        "topics": topics,
        "back_url": "/listening/part-4/",
        "topic_url_prefix": "/listening/part-4/may-kem/",
    })


# Alias phòng khi code cũ gọi may-dot
def student_part2_dot_topics(request):
    return student_part2_kem_topics(request)
# ===== End fix student Part 2 topic list routes =====


# ===== FINAL FIX: Part 2 May Gioi dropdown options from total data =====
def _is_admin_user_part2_gioi_dropdown(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_4_person_dropdown(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Person {i}"
            )

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _split_total_answer_options(topic):
    return [
        line.strip()
        for line in (topic.data_choices or "").splitlines()
        if line.strip()
    ]


@csrf_exempt
@user_passes_test(_is_admin_user_part2_gioi_dropdown)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_4_person_dropdown(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_total_answers":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.voice_info = request.POST.get("voice_info", "").strip()
        topic.save()

        for voice in voices:
            voice.audio_url = topic.audio_url
            voice.question_text = f"Person {voice.order}"
            voice.save()

        messages.success(request, "Đã lưu dữ liệu đáp án tổng. Bây giờ bạn có thể chọn đáp án đúng cho từng Person.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "save_topic":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.voice_info = request.POST.get("voice_info", "").strip()
        topic.save()

        # Lưu đáp án đúng từng person
        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = f"Person {voice.order}"
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu. Các lựa chọn đáp án đã được cập nhật từ dữ liệu đáp án tổng.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = _split_total_answer_options(topic)

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_4_person_dropdown(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _split_total_answer_options(topic)

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== END FINAL FIX: Part 2 May Gioi dropdown options from total data =====


# ===== FINAL OVERRIDE May Gioi save total answers button =====
def _is_admin_user_part2_gioi_save_total(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_four_person_save_total(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(
                topic=topic,
                order=i,
                question_text=f"Person {i}"
            )

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _gioi_total_options_save_total(topic):
    return [
        x.strip()
        for x in (topic.data_choices or "").splitlines()
        if x.strip()
    ]


@csrf_exempt
@user_passes_test(_is_admin_user_part2_gioi_save_total)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_save_total(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_total_answers":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.voice_info = request.POST.get("voice_info", "").strip()
        topic.save()

        for voice in voices:
            voice.question_text = f"Person {voice.order}"
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu đáp án tổng. Bây giờ có thể chọn đáp án đúng cho Person 1-4.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "save_correct_answers":
        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = f"Person {voice.order}"
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu đáp án đúng cho 4 Person.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = _gioi_total_options_save_total(topic)

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_save_total(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _gioi_total_options_save_total(topic)

    rows = []
    for voice in voices:
        rows.append({
            "voice": voice,
            "options": options,
        })

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== END FINAL OVERRIDE May Gioi save total answers button =====


# ===== FINAL FIX voice_info + correct answers for May Gioi =====
def _is_admin_user_part2_gioi_voice_info_final(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_four_person_voice_info_final(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(topic=topic, order=i, question_text=f"Person {i}")

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _gioi_options_voice_info_final(topic):
    return [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]


@user_passes_test(_is_admin_user_part2_gioi_voice_info_final)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_info_final(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST" and request.POST.get("action") == "save_total_answers":
        topic.title = request.POST.get("title", "").strip() or topic.title
        topic.description = request.POST.get("description", "").strip()
        topic.audio_url = request.POST.get("audio_url", "").strip()
        topic.data_choices = request.POST.get("data_choices", "").strip()
        topic.voice_info = request.POST.get("voice_info", "").strip()
        topic.save()

        for voice in voices:
            voice.question_text = f"Person {voice.order}"
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu đáp án tổng và thông tin voice.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    if request.method == "POST" and request.POST.get("action") == "save_correct_answers":
        for voice in voices:
            prefix = f"voice_{voice.id}_"
            voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
            voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
            voice.question_text = f"Person {voice.order}"
            voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
            voice.audio_url = topic.audio_url
            voice.save()

        messages.success(request, "Đã lưu đáp án đúng cho 4 Person.")
        return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = _gioi_options_voice_info_final(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_info_final(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _gioi_options_voice_info_final(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== END FINAL FIX voice_info + correct answers for May Gioi =====


# ===== FINAL: May Gioi voice info input + lock =====
def _is_admin_user_part2_gioi_voice_lock(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _ensure_gioi_four_person_voice_lock(topic):
    existing_orders = set(topic.voices.values_list("order", flat=True))
    for i in range(1, 5):
        if i not in existing_orders:
            Part2Voice.objects.create(topic=topic, order=i, question_text=f"Person {i}")

    topic.voices.exclude(order__in=[1, 2, 3, 4]).delete()

    for voice in topic.voices.filter(order__in=[1, 2, 3, 4]):
        voice.question_text = f"Person {voice.order}"
        voice.audio_url = topic.audio_url
        voice.save()


def _gioi_options_voice_lock(topic):
    return [x.strip() for x in (topic.data_choices or "").splitlines() if x.strip()]


@user_passes_test(_is_admin_user_part2_gioi_voice_lock)
def admin_part2_gioi_detail(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_lock(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "save_total_answers":
            topic.title = request.POST.get("title", "").strip() or topic.title
            topic.description = request.POST.get("description", "").strip()
            topic.audio_url = request.POST.get("audio_url", "").strip()
            topic.data_choices = request.POST.get("data_choices", "").strip()

            # Chỉ cập nhật voice_info nếu chưa khóa
            if not getattr(topic, "voice_info_locked", False):
                topic.voice_info = request.POST.get("voice_info", "").strip()

            topic.save()

            for voice in voices:
                voice.question_text = f"Person {voice.order}"
                voice.audio_url = topic.audio_url
                voice.save()

            messages.success(request, "Đã lưu đáp án tổng.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

        if action == "save_and_lock_voice_info":
            if not getattr(topic, "voice_info_locked", False):
                topic.voice_info = request.POST.get("voice_info", "").strip()
                topic.voice_info_locked = True
                topic.save()
                messages.success(request, "Đã lưu và khóa thông tin voice.")
            else:
                messages.warning(request, "Thông tin voice đang bị khóa.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

        if action == "unlock_voice_info":
            topic.voice_info_locked = False
            topic.save()
            messages.success(request, "Đã mở khóa thông tin voice. Bây giờ có thể sửa lại.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

        if action == "save_correct_answers":
            for voice in voices:
                prefix = f"voice_{voice.id}_"
                voice.is_locked = request.POST.get(prefix + "is_locked") == "on"
                voice.order = int(request.POST.get(prefix + "order", voice.order) or voice.order)
                voice.question_text = f"Person {voice.order}"
                voice.correct_data = request.POST.get(prefix + "correct_data", "").strip()
                voice.audio_url = topic.audio_url
                voice.save()

            messages.success(request, "Đã lưu đáp án đúng cho 4 Person.")
            return redirect("admin_part2_gioi_detail", topic_id=topic.id)

    options = _gioi_options_voice_lock(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/admin_part2_gioi_detail.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })


def student_part2_gioi_page(request, topic_id):
    topic = get_object_or_404(Part2Topic, id=topic_id, version="gioi")
    _ensure_gioi_four_person_voice_lock(topic)

    voices = list(topic.voices.all().order_by("order", "id")[:4])
    options = _gioi_options_voice_lock(topic)
    rows = [{"voice": voice, "options": options} for voice in voices]

    return render(request, "core/student_part2_gioi.html", {
        "topic": topic,
        "rows": rows,
        "options": options,
    })
# ===== END FINAL: May Gioi voice info input + lock =====


# ===== Listening Part 3/4 material upload + student practice =====
def _is_admin_user_part34(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _part34_question_options(question, include_blank=True):
    options = [
        ("A", question.option_a),
        ("B", question.option_b),
        ("C", question.option_c),
        ("D", question.option_d),
        ("E", question.option_e),
        ("F", question.option_f),
    ]
    if include_blank:
        return options
    return [(label, text) for label, text in options if str(text or "").strip()]


def _part34_question_rows(material, include_blank=True):
    if not material:
        return []

    return [
        {
            "question": question,
            "options": _part34_question_options(question, include_blank=include_blank),
        }
        for question in material.questions.all().order_by("order", "id")
    ]


def _part34_redirect(request, material_id=None):
    if material_id:
        return redirect(f"{request.path}?material={material_id}")
    return redirect(request.path)


def _admin_part34_page(request, part_number):
    materials = ListeningPartMaterial.objects.filter(part=part_number).prefetch_related("questions").order_by("id")

    if request.method == "POST":
        action = request.POST.get("action", "").strip()
        material_id = request.POST.get("material_id")

        if action == "create_material":
            material = ListeningPartMaterial.objects.create(
                part=part_number,
                title=request.POST.get("title", "").strip() or f"Listening Part {part_number}",
                description=request.POST.get("description", "").strip(),
                instructions=request.POST.get("instructions", "").strip(),
                audio_url=request.POST.get("audio_url", "").strip(),
                transcript=request.POST.get("transcript", "").strip(),
                is_active=request.POST.get("is_active") == "on",
            )
            document_file = request.FILES.get("document_file")
            if document_file:
                material.document_file = document_file
                material.save()

            messages.success(request, f"Đã tạo tài liệu Part {part_number}.")
            return _part34_redirect(request, material.id)

        material = get_object_or_404(ListeningPartMaterial, id=material_id, part=part_number)

        if action == "save_material":
            material.title = request.POST.get("title", "").strip() or material.title
            material.description = request.POST.get("description", "").strip()
            material.instructions = request.POST.get("instructions", "").strip()
            material.audio_url = request.POST.get("audio_url", "").strip()
            material.transcript = request.POST.get("transcript", "").strip()
            material.is_active = request.POST.get("is_active") == "on"

            document_file = request.FILES.get("document_file")
            if document_file:
                material.document_file = document_file
            if request.POST.get("clear_document") == "on" and material.document_file:
                material.document_file.delete(save=False)
                material.document_file = None

            material.save()
            messages.success(request, "Đã lưu tài liệu.")
            return _part34_redirect(request, material.id)

        if action == "delete_material":
            material.delete()
            messages.success(request, "Đã xóa tài liệu.")
            return _part34_redirect(request)

        if action == "add_question":
            last_question = material.questions.order_by("-order", "-id").first()
            next_order = (last_question.order + 1) if last_question else 1
            ListeningPartQuestion.objects.create(
                material=material,
                order=next_order,
                question_text=f"Câu {next_order}",
            )
            messages.success(request, "Đã thêm câu hỏi mới.")
            return _part34_redirect(request, material.id)

        if action == "save_questions":
            delete_question_id = request.POST.get("delete_question")
            if delete_question_id:
                ListeningPartQuestion.objects.filter(id=delete_question_id, material=material).delete()
                messages.success(request, "Đã xóa câu hỏi.")
                return _part34_redirect(request, material.id)

            valid_answers = {"A", "B", "C", "D", "E", "F"}
            for question_id in request.POST.getlist("question_id"):
                question = ListeningPartQuestion.objects.filter(id=question_id, material=material).first()
                if not question:
                    continue

                prefix = f"question_{question.id}_"
                try:
                    question.order = int(request.POST.get(prefix + "order", question.order) or question.order)
                except ValueError:
                    pass

                question.question_text = request.POST.get(prefix + "question_text", "").strip() or question.question_text
                question.option_a = request.POST.get(prefix + "option_a", "").strip()
                question.option_b = request.POST.get(prefix + "option_b", "").strip()
                question.option_c = request.POST.get(prefix + "option_c", "").strip()
                question.option_d = request.POST.get(prefix + "option_d", "").strip()
                question.option_e = request.POST.get(prefix + "option_e", "").strip()
                question.option_f = request.POST.get(prefix + "option_f", "").strip()
                answer = request.POST.get(prefix + "correct_answer", "A").strip().upper()
                question.correct_answer = answer if answer in valid_answers else "A"
                question.explanation = request.POST.get(prefix + "explanation", "").strip()
                question.save()

            messages.success(request, "Đã lưu câu hỏi và đáp án.")
            return _part34_redirect(request, material.id)

    selected = None
    selected_id = request.GET.get("material")
    if selected_id:
        selected = materials.filter(id=selected_id).first()
    if not selected:
        selected = materials.first()

    return render(request, "core/admin_part34_materials.html", {
        "part_number": part_number,
        "part_title": f"Listening Part {part_number}",
        "materials": materials,
        "selected": selected,
        "question_rows": _part34_question_rows(selected),
        "answer_labels": ["A", "B", "C", "D", "E", "F"],
    })


def _part34_student_identity(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    student_id = ""
    student_name = request.user.get_full_name() or request.user.username
    student_email = request.user.email or request.user.username

    if profile:
        student_id = profile.student_id or profile.id
        student_name = profile.full_name or student_name
        student_email = profile.email or student_email
    else:
        student_id = request.user.id

    return {
        "student_id": student_id,
        "student_name": student_name,
        "student_email": student_email,
        "student_watermark": f"ID {student_id} - {student_name} - {student_email}",
    }


def _student_part34_page(request, part_number):
    materials = ListeningPartMaterial.objects.filter(part=part_number, is_active=True).prefetch_related("questions").order_by("id")

    selected = None
    selected_id = request.GET.get("material")
    if selected_id:
        selected = materials.filter(id=selected_id).first()
    if not selected:
        selected = materials.first()

    is_checked = request.method == "POST" and request.POST.get("action") == "check_answers"
    question_rows = _part34_question_rows(selected, include_blank=False)
    for row in question_rows:
        question = row["question"]
        selected_answer = request.POST.get(f"question_{question.id}", "").strip().upper() if is_checked else ""
        row["is_checked"] = is_checked
        row["selected_answer"] = selected_answer
        row["is_correct"] = bool(selected_answer and selected_answer == question.correct_answer)

    context = {
        "part_number": part_number,
        "part_title": f"Listening Part {part_number}",
        "materials": materials,
        "selected": selected,
        "question_rows": question_rows,
        "is_checked": is_checked,
    }
    context.update(_part34_student_identity(request))

    return render(request, "core/student_part34.html", context)


@user_passes_test(_is_admin_user_part34)
def admin_part3_questions(request):
    return _admin_part34_page(request, 3)


@user_passes_test(_is_admin_user_part34)

@login_required
def student_part3_page(request):
    return _student_part34_page(request, 3)


@login_required

@login_required
def admin_part3_questions(request):
    is_admin_user = (
        request.user.is_staff
        or request.user.is_superuser
        or request.user.username == "admin"
        or request.user.email == "admin@gmail.com"
    )

    if not is_admin_user:
        return redirect("listening")

    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "create_material":
            material = ListeningPartMaterial.objects.create(
                part=3,
                title="Những thay đổi tại nơi làm việc",
                description="Bộ câu hỏi nghe Part 3",
                instructions="Nghe hai người thảo luận về những thay đổi liên quan đến chủ đề bên trên. Đọc các nhận định và chọn xem ý kiến đó thuộc về người nam, người nữ hay cả hai.`nAi thể hiện ý kiến nào?",
                is_active=True,
            )

            sample_questions = [
                "Sự ổn định rất quan trọng khi lập kế hoạch nghề nghiệp",
                "Sự đảm bảo công việc không thể được chắc chắn",
                "Sự hài lòng trong công việc là động lực quan trọng",
                "Cải tiến công nghệ có lợi cho nền kinh tế",
            ]

            for index, text in enumerate(sample_questions, start=1):
                ListeningPartQuestion.objects.create(
                    material=material,
                    order=index,
                    question_text=text,
                    option_a="Người nam",
                    option_b="Người nữ",
                    option_c="Cả hai",
                    correct_answer="A",
                )

            messages.success(request, "Đã tạo bộ Part 3 mới.")
            return redirect(f"{request.path}?material_id={material.id}")

        material_id = request.POST.get("material_id")
        material = get_object_or_404(ListeningPartMaterial, id=material_id, part=3)

        if action == "delete_material":
            material.delete()
            messages.success(request, "Đã xóa bộ Part 3.")
            return redirect("admin_part3_questions")

        if action == "save_material":
            material.title = request.POST.get("title", "").strip() or material.title
            material.audio_url = request.POST.get("audio_url", "").strip()
            material.instructions = request.POST.get("instructions", "").strip()
            material.transcript = request.POST.get("transcript", "").strip()
            material.is_active = request.POST.get("is_active") == "1"
            material.save()

            question_ids = request.POST.getlist("question_id")

            for position, question_id in enumerate(question_ids, start=1):
                question = ListeningPartQuestion.objects.filter(id=question_id, material=material).first()
                if not question:
                    continue

                question.order = position
                question.question_text = request.POST.get(f"question_text_{question.id}", "").strip()
                question.option_a = request.POST.get(f"option_a_{question.id}", "Người nam").strip() or "Người nam"
                question.option_b = request.POST.get(f"option_b_{question.id}", "Người nữ").strip() or "Người nữ"
                question.option_c = request.POST.get(f"option_c_{question.id}", "Cả hai").strip() or "Cả hai"
                question.correct_answer = request.POST.get(f"correct_answer_{question.id}", "A").strip()[:1] or "A"
                question.explanation = request.POST.get(f"explanation_{question.id}", "").strip()
                question.save()

            messages.success(request, "Đã lưu bộ Part 3.")
            return redirect(f"{request.path}?material_id={material.id}")

    materials = ListeningPartMaterial.objects.filter(part=3).prefetch_related("questions").order_by("id")

    selected = None
    selected_id = request.GET.get("material_id")

    if selected_id:
        selected = materials.filter(id=selected_id).first()

    if selected is None:
        selected = materials.first()

    questions = []

    if selected:
        questions = list(selected.questions.all().order_by("order", "id"))

        while len(questions) < 4:
            q = ListeningPartQuestion.objects.create(
                material=selected,
                order=len(questions) + 1,
                question_text=f"Statement {len(questions) + 1}",
                option_a="Người nam",
                option_b="Người nữ",
                option_c="Cả hai",
                correct_answer="A",
            )
            questions.append(q)

        questions = questions[:4]

    return render(request, "core/admin_part3_questions.html", {
        "materials": materials,
        "selected": selected,
        "questions": questions,
    })


@login_required
def student_part3_page(request):
    materials = list(
        ListeningPartMaterial.objects
        .filter(part=3, is_active=True)
        .prefetch_related("questions")
        .order_by("id")
    )

    total_questions = sum(max(4, item.questions.count()) for item in materials)

    try:
        set_index = int(request.GET.get("set", "0"))
    except ValueError:
        set_index = 0

    if set_index < 0:
        set_index = 0

    if materials and set_index >= len(materials):
        set_index = len(materials) - 1

    selected = materials[set_index] if materials else None
    questions = []
    start_number = 1

    if selected:
        for item in materials[:set_index]:
            start_number += max(4, item.questions.count())

        raw_questions = list(selected.questions.all().order_by("order", "id"))[:4]

        for index, question in enumerate(raw_questions, start=start_number):
            question.display_number = index
            questions.append(question)

    return render(request, "core/listening_part3.html", {
        "materials": materials,
        "selected": selected,
        "questions": questions,
        "total_questions": total_questions or 0,
        "start_number": start_number,
        "prev_index": max(0, set_index - 1),
        "next_index": min(len(materials) - 1, set_index + 1) if materials else 0,
        "has_prev": set_index > 0,
        "has_next": bool(materials) and set_index < len(materials) - 1,
    })
# === TSA PART 3 FULL INTEGRATION END ===


# ===== Real Listening Part 4 admin/student interface =====

def student_part4_page(request):
    all_materials = ListeningPartMaterial.objects.filter(part=4, is_active=True).order_by("id")

    # Only show real Part 4 rows that have at least one usable question/answer/paraphrase.
    valid_ids = []
    for material in all_materials:
        q16 = material.questions.filter(order=16).first()
        q17 = material.questions.filter(order=17).first()

        has_q16_data = q16 and (
            (q16.question_text or "").strip()
            and (
                (q16.option_a or "").strip()
                or (q16.option_b or "").strip()
                or (q16.option_c or "").strip()
            )
        )

        has_q17_data = q17 and (
            (q17.question_text or "").strip()
            and (
                (q17.option_a or "").strip()
                or (q17.option_b or "").strip()
                or (q17.option_c or "").strip()
            )
        )

        has_paraphrase = bool((material.transcript or "").strip())

        if has_q16_data or has_q17_data or has_paraphrase:
            valid_ids.append(material.id)

    materials = all_materials.filter(id__in=valid_ids).order_by("id")

    selected_id = request.GET.get("set")
    selected = None

    if selected_id:
        selected = materials.filter(id=selected_id).first()

    if selected is None:
        selected = materials.first()

    questions = selected.questions.filter(order__in=[16, 17]).order_by("order", "id") if selected else []

    return render(request, "core/student_part4.html", {
        "materials": materials,
        "selected": selected,
        "questions": questions,
    })


# ===== End Student Listening Part 4 Aptis Keys style interface =====


# ===== Real Listening Part 4 table admin interface =====
def _is_admin_user_part4(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.username == "admin")


def _ensure_part4_pair(material):
    q16, _ = ListeningPartQuestion.objects.get_or_create(
        material=material,
        order=16,
        defaults={
            "question_text": "Question 16",
            "option_a": "",
            "option_b": "",
            "option_c": "",
            "correct_answer": "A",
        }
    )

    q17, _ = ListeningPartQuestion.objects.get_or_create(
        material=material,
        order=17,
        defaults={
            "question_text": "Question 17",
            "option_a": "",
            "option_b": "",
            "option_c": "",
            "correct_answer": "A",
        }
    )

    return q16, q17


@csrf_exempt
@user_passes_test(_is_admin_user_part4)
def admin_part4_questions(request):
    if request.method == "POST":
        action = request.POST.get("action", "")

        if action == "create_row":
            material = ListeningPartMaterial.objects.create(
                part=4,
                title="New Topic",
                description="Question set",
                instructions="Listen to the audio and choose the correct answer.",
                audio_url="",
                transcript="",
                is_active=True,
            )

            _ensure_part4_pair(material)

            messages.success(request, "Created a new Part 4 row.")
            return redirect("admin_part4_questions")

        if request.POST.get("delete_one"):
            material_id = request.POST.get("delete_one")
            ListeningPartMaterial.objects.filter(id=material_id, part=4).delete()
            messages.success(request, "Deleted one Part 4 row.")
            return redirect("admin_part4_questions")

        if action == "save_all" or request.POST.get("save_one"):
            target_ids = request.POST.getlist("material_id")

            if request.POST.get("save_one"):
                target_ids = [request.POST.get("save_one")]

            for material_id in target_ids:
                material = ListeningPartMaterial.objects.filter(id=material_id, part=4).first()
                if not material:
                    continue

                material.audio_url = request.POST.get(f"audio_url_{material.id}", "").strip()
                material.description = request.POST.get(f"question_label_{material.id}", "").strip()
                material.title = request.POST.get(f"topic_{material.id}", "").strip() or "Untitled Topic"
                material.transcript = request.POST.get(f"paraphrase_{material.id}", "").strip()
                material.instructions = "Listen to the audio and choose the correct answer."
                material.is_active = True
                material.save()

                q16, q17 = _ensure_part4_pair(material)

                q16.question_text = request.POST.get(f"q16_text_{material.id}", "").strip()
                q16.option_a = request.POST.get(f"q16_a_{material.id}", "").strip()
                q16.option_b = request.POST.get(f"q16_b_{material.id}", "").strip()
                q16.option_c = request.POST.get(f"q16_c_{material.id}", "").strip()
                q16.option_d = ""
                q16.option_e = ""
                q16.option_f = ""
                q16_correct = request.POST.get(f"q16_correct_{material.id}", "A").strip().upper()[:1] or "A"
                q16.correct_answer = q16_correct if q16_correct in ["A", "B", "C"] else "A"
                q16.save()

                q17.question_text = request.POST.get(f"q17_text_{material.id}", "").strip()
                q17.option_a = request.POST.get(f"q17_a_{material.id}", "").strip()
                q17.option_b = request.POST.get(f"q17_b_{material.id}", "").strip()
                q17.option_c = request.POST.get(f"q17_c_{material.id}", "").strip()
                q17.option_d = ""
                q17.option_e = ""
                q17.option_f = ""
                q17_correct = request.POST.get(f"q17_correct_{material.id}", "A").strip().upper()[:1] or "A"
                q17.correct_answer = q17_correct if q17_correct in ["A", "B", "C"] else "A"
                q17.save()

            messages.success(request, "Saved Part 4 table data.")
            return redirect("admin_part4_questions")

    materials = ListeningPartMaterial.objects.filter(part=4).order_by("id")

    rows = []
    audio_count = 0
    q16_count = 0
    q17_count = 0

    for material in materials:
        q16, q17 = _ensure_part4_pair(material)

        if material.audio_url:
            audio_count += 1

        if q16.question_text:
            q16_count += 1

        if q17.question_text:
            q17_count += 1

        rows.append({
            "material": material,
            "q16": q16,
            "q17": q17,
        })

    return render(request, "core/admin_part4_questions.html", {
        "rows": rows,
        "total_rows": materials.count(),
        "audio_count": audio_count,
        "q16_count": q16_count,
        "q17_count": q17_count,
    })
# ===== End real Listening Part 4 table admin interface =====

