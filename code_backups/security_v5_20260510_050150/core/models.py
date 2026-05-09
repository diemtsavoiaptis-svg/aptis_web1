from django.db import models
from django.contrib.auth.models import User


def _vi(text):
    return text.encode("ascii").decode("unicode_escape")


class StudentProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', _vi(r"Ch\u1edd duy\u1ec7t")),
        ('approved', _vi(r"\u0110\u00e3 duy\u1ec7t")),
        ('rejected', _vi(r"T\u1eeb ch\u1ed1i")),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_vi(r"T\u00e0i kho\u1ea3n"))
    full_name = models.CharField(max_length=150, verbose_name=_vi(r"H\u1ecd t\u00ean h\u1ecdc vi\u00ean"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_vi(r"S\u1ed1 \u0111i\u1ec7n tho\u1ea1i"))
    email = models.EmailField(verbose_name="Email")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_vi(r"Tr\u1ea1ng th\u00e1i")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_vi(r"Ng\u00e0y \u0111\u0103ng k\u00fd"))

    class Meta:
        verbose_name = _vi(r"H\u1ecdc vi\u00ean")
        verbose_name_plural = _vi(r"Danh s\u00e1ch h\u1ecdc vi\u00ean")

    def __str__(self):
        return self.full_name


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name=_vi(r"Ti\u00eau \u0111\u1ec1 b\u00e0i h\u1ecdc"))
    description = models.TextField(blank=True, verbose_name=_vi(r"M\u00f4 t\u1ea3"))
    content = models.TextField(blank=True, verbose_name=_vi(r"N\u1ed9i dung"))
    video_url = models.URLField(blank=True, verbose_name=_vi(r"Link video"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_vi(r"Ng\u00e0y t\u1ea1o"))

    class Meta:
        verbose_name = _vi(r"B\u00e0i h\u1ecdc")
        verbose_name_plural = _vi(r"Danh s\u00e1ch b\u00e0i h\u1ecdc")

    def __str__(self):
        return self.title


class ListeningQuestion(models.Model):
    PART_CHOICES = [
        (1, "Part 1"),
        (2, "Part 2"),
        (3, "Part 3"),
        (4, "Part 4"),
    ]

    ANSWER_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
    ]

    part = models.IntegerField(choices=PART_CHOICES, default=1, verbose_name="Part")
    question_number = models.IntegerField(verbose_name=_vi(r"S\u1ed1 c\u00e2u"))
    question_text = models.TextField(verbose_name=_vi(r"C\u00e2u h\u1ecfi"))
    audio_url = models.URLField(blank=True, verbose_name=_vi(r"Link audio ngo\u00e0i"))
    audio_file = models.FileField(upload_to='listening_audio/', blank=True, null=True, verbose_name=_vi(r"File audio t\u1ea3i l\u00ean"))

    option_a = models.CharField(max_length=255, verbose_name=_vi(r"\u0110\u00e1p \u00e1n A"))
    option_b = models.CharField(max_length=255, verbose_name=_vi(r"\u0110\u00e1p \u00e1n B"))
    option_c = models.CharField(max_length=255, verbose_name=_vi(r"\u0110\u00e1p \u00e1n C"))

    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
        default='A',
        verbose_name=_vi(r"\u0110\u00e1p \u00e1n \u0111\u00fang")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_vi(r"Ng\u00e0y t\u1ea1o"))

    class Meta:
        verbose_name = _vi(r"C\u00e2u h\u1ecfi Listening")
        verbose_name_plural = _vi(r"Danh s\u00e1ch c\u00e2u h\u1ecfi Listening")
        ordering = ['part', 'question_number']

    def __str__(self):
        return f"Part {self.part} - " + _vi(r"C\u00e2u") + f" {self.question_number}"


class HomeBackground(models.Model):
    title = models.CharField(
        max_length=150,
        default=_vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7"),
        verbose_name=_vi(r"T\u00ean \u1ea3nh")
    )
    image = models.FileField(upload_to='home_backgrounds/', verbose_name=_vi(r"\u1ea2nh n\u1ec1n"))
    is_active = models.BooleanField(default=True, verbose_name=_vi(r"\u0110ang s\u1eed d\u1ee5ng"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_vi(r"Ng\u00e0y t\u1ea3i l\u00ean"))

    class Meta:
        verbose_name = _vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7")
        verbose_name_plural = _vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7")

    def __str__(self):
        return self.title
