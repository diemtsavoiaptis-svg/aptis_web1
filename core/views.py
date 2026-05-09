from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import StudentProfile, Lesson, ListeningQuestion, HomeBackground


def home(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    home_background = HomeBackground.objects.filter(is_active=True).order_by('-created_at').first()

    return render(request, 'core/home.html', {
        'login_form': login_form,
        'register_form': register_form,
        'home_background': home_background,
    })


def register_view(request):
    if request.method != 'POST':
        return redirect('home')

    form = RegisterForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Thông tin đăng ký chưa hợp lệ.')
        return redirect('home')

    full_name = form.cleaned_data['full_name']
    phone = form.cleaned_data['phone']
    email = form.cleaned_data['email']
    password = form.cleaned_data['password']

    if User.objects.filter(username=email).exists():
        messages.error(request, 'Email này đã được đăng ký.')
        return redirect('home')

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
        status='pending'
    )

    messages.success(request, 'Đăng ký thành công. Vui lòng chờ admin duyệt tài khoản.')
    return redirect('home')


def login_view(request):
    if request.method != 'POST':
        return redirect('home')

    form = LoginForm(request.POST)

    if not form.is_valid():
        messages.error(request, 'Thông tin đăng nhập chưa hợp lệ.')
        return redirect('home')

    email = form.cleaned_data['email']
    password = form.cleaned_data['password']

    user_check = User.objects.filter(username=email).first()

    if user_check and not user_check.is_active:
        messages.error(request, 'Tài khoản của bạn đang chờ admin duyệt.')
        return redirect('home')

    user = authenticate(request, username=email, password=password)

    if user is None:
        messages.error(request, 'Email hoặc mật khẩu không đúng.')
        return redirect('home')

    login(request, user)
    return redirect('dashboard')


@login_required
def dashboard(request):
    lessons = Lesson.objects.all().order_by('-created_at')

    return render(request, 'core/dashboard.html', {
        'lessons': lessons
    })


@login_required
def listening_view(request):
    part = int(request.GET.get('part', 1))
    questions = ListeningQuestion.objects.filter(part=part).order_by('question_number')
    parts = [1, 2, 3, 4]

    return render(request, 'core/listening.html', {
        'part': part,
        'parts': parts,
        'questions': questions,
        'total_questions': questions.count(),
    })


def logout_view(request):
    logout(request)
    return redirect('home')
