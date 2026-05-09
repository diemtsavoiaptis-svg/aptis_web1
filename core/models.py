from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Tài khoản')
    full_name = models.CharField(max_length=150, verbose_name='Họ tên học viên')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Số điện thoại')
    email = models.EmailField(verbose_name='Email')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đăng ký')

    class Meta:
        verbose_name = 'Học viên'
        verbose_name_plural = 'Danh sách học viên'

    def __str__(self):
        return self.full_name


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Tiêu đề bài học')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    content = models.TextField(blank=True, verbose_name='Nội dung')
    video_url = models.URLField(blank=True, verbose_name='Link video')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Bài học'
        verbose_name_plural = 'Danh sách bài học'

    def __str__(self):
        return self.title


class ListeningQuestion(models.Model):
    PART_CHOICES = [
        (1, 'Part 1'),
        (2, 'Part 2'),
        (3, 'Part 3'),
        (4, 'Part 4'),
    ]

    ANSWER_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]

    part = models.IntegerField(choices=PART_CHOICES, default=1, verbose_name='Part')
    question_number = models.IntegerField(verbose_name='Số câu')
    question_text = models.TextField(verbose_name='Câu hỏi')
    audio_url = models.URLField(blank=True, verbose_name='Link audio')

    option_a = models.CharField(max_length=255, verbose_name='Đáp án A')
    option_b = models.CharField(max_length=255, verbose_name='Đáp án B')
    option_c = models.CharField(max_length=255, verbose_name='Đáp án C')

    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        default='A',
        verbose_name='Đáp án đúng'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Câu hỏi Listening'
        verbose_name_plural = 'Danh sách câu hỏi Listening'
        ordering = ['part', 'question_number']

    def __str__(self):
        return f'Part {self.part} - Câu {self.question_number}'



class HomeBackground(models.Model):
    title = models.CharField(max_length=150, default='?nh n?n trang ch?', verbose_name='T?n ?nh')
    image = models.FileField(upload_to='home_backgrounds/', verbose_name='?nh n?n')
    is_active = models.BooleanField(default=True, verbose_name='?ang s? d?ng')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ng?y t?i l?n')

    class Meta:
        verbose_name = '?nh n?n trang ch?'
        verbose_name_plural = '?nh n?n trang ch?'

    def __str__(self):
        return self.title
