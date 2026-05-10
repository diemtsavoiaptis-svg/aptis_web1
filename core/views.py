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
from .models import StudentProfile, Lesson, ListeningQuestion, HomeBackground, SecurityAlert
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
