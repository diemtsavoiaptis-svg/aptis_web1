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
        messages.error(request, "Th?ng tin ??ng k? ch?a h?p l?.")
        return redirect("home")

    full_name = form.cleaned_data["full_name"]
    phone = form.cleaned_data["phone"]
    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]

    if User.objects.filter(username=email).exists():
        messages.error(request, "Email n?y ?? ???c ??ng k?.")
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

    messages.success(request, "??ng k? th?nh c?ng. Vui l?ng ch? admin duy?t t?i kho?n.")
    return redirect("home")


def login_view(request):
    if request.method != "POST":
        return redirect("home")

    ip = get_client_ip(request) or "unknown"
    throttle_key = f"login_fail:{ip}"
    fail_count = cache.get(throttle_key, 0)

    if fail_count >= 8:
        messages.error(request, "B?n ??ng nh?p sai qu? nhi?u l?n. Vui l?ng th? l?i sau 15 ph?t.")
        return redirect("home")

    form = LoginForm(request.POST)

    if not form.is_valid():
        cache.set(throttle_key, fail_count + 1, 60 * 15)
        messages.error(request, "Th?ng tin ??ng nh?p ch?a h?p l?.")
        return redirect("home")

    email = form.cleaned_data["email"]
    password = form.cleaned_data["password"]

    user_check = User.objects.filter(username=email).first()

    if user_check and not user_check.is_active:
        messages.error(request, "T?i kho?n c?a b?n ?ang ch? admin duy?t.")
        return redirect("home")

    user = authenticate(request, username=email, password=password)

    if user is None:
        cache.set(throttle_key, fail_count + 1, 60 * 15)

        target_user = User.objects.filter(username=email).first()

        if target_user:
            SecurityAlert.objects.get_or_create(
                user=target_user,
                reason="C? nhi?u l?n ??ng nh?p sai m?t kh?u",
                ip_address=ip,
                is_resolved=False,
                defaults={
                    "severity": "medium",
                    "user_agent": request.META.get("HTTP_USER_AGENT", "")[:1000],
                }
            )

        messages.error(request, "Email ho?c m?t kh?u kh?ng ??ng.")
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

    # Google Drive ??i khi y?u c?u confirm token cho file l?n / b? qu?t virus.
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
        raise Http404("Kh?ng t?i ???c audio t? Google Drive.")

    # N?u Google tr? v? HTML th? ngh?a l? link Drive ch?a public ho?c b? ch?n t?i tr?c ti?p.
    if "text/html" in content_type.lower():
        raise Http404("Google Drive ch?a tr? v? file MP3 tr?c ti?p. H?y b?t chia s? file: B?t k? ai c? ???ng li?n k?t ? Ng??i xem.")

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

    return render(request, "core/dashboard.html", {
        "lessons": lessons
    })


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

    raise Http404("Audio kh?ng t?n t?i.")

@login_required
@require_POST
def security_event_view(request):
    event_type = request.POST.get("event_type", "unknown")[:120]
    severity = request.POST.get("severity", "medium")[:20]

    if severity not in ["low", "medium", "high", "critical"]:
        severity = "medium"

    reason_map = {
        "print_attempt": "H?c vi?n c? g?ng in ho?c l?u PDF",
        "save_attempt": "H?c vi?n c? g?ng l?u trang",
        "source_attempt": "H?c vi?n c? g?ng xem m? ngu?n trang",
        "devtools_attempt": "H?c vi?n c? d?u hi?u m? c?ng c? ki?m tra trang",
        "tab_blur": "H?c vi?n r?i kh?i tab l?m b?i",
        "screenshot_key": "H?c vi?n b?m ph?m Print Screen",
    }

    reason = reason_map.get(event_type, f"S? ki?n b?o m?t: {event_type}")

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
