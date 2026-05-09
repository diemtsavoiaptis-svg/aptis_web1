from django.contrib import admin
from django.utils.html import format_html
from .models import StudentProfile, Lesson, ListeningQuestion, HomeBackground


def _vi(text):
    return text.encode("ascii").decode("unicode_escape")


admin.site.site_header = _vi(r"Qu\u1ea3n tr\u1ecb TSA Aptis")
admin.site.site_title = "TSA Aptis Admin"
admin.site.index_title = _vi(r"Site qu\u1ea3n tr\u1ecb h\u1ec7 th\u1ed1ng")


@admin.action(description=_vi(r"Duy\u1ec7t h\u1ecdc vi\u00ean \u0111\u00e3 ch\u1ecdn"))
def approve_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = 'approved'
        student.save()
        student.user.is_active = True
        student.user.save()


@admin.action(description=_vi(r"T\u1eeb ch\u1ed1i h\u1ecdc vi\u00ean \u0111\u00e3 ch\u1ecdn"))
def reject_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = 'rejected'
        student.save()
        student.user.is_active = False
        student.user.save()


@admin.action(description=_vi(r"\u0110\u01b0a h\u1ecdc vi\u00ean v\u1ec1 tr\u1ea1ng th\u00e1i ch\u1edd duy\u1ec7t"))
def pending_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = 'pending'
        student.save()
        student.user.is_active = False
        student.user.save()


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status_badge', 'account_status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'user__username')
    actions = [approve_students, reject_students, pending_students]
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        (_vi(r"Th\u00f4ng tin h\u1ecdc vi\u00ean"), {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        (_vi(r"Tr\u1ea1ng th\u00e1i x\u00e9t duy\u1ec7t"), {
            'fields': ('status', 'created_at')
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'approved': '#12a150',
            'rejected': '#d40000',
        }
        labels = {
            'pending': _vi(r"Ch\u1edd duy\u1ec7t"),
            'approved': _vi(r"\u0110\u00e3 duy\u1ec7t"),
            'rejected': _vi(r"T\u1eeb ch\u1ed1i"),
        }
        return format_html(
            '<span class="tsa-badge" style="background:{};">{}</span>',
            colors.get(obj.status, '#555'),
            labels.get(obj.status, obj.status)
        )

    status_badge.short_description = _vi(r"Tr\u1ea1ng th\u00e1i")

    def account_status(self, obj):
        if obj.user.is_active:
            return format_html('<span class="tsa-soft-badge green">{}</span>', _vi(r"\u0110ang ho\u1ea1t \u0111\u1ed9ng"))
        return format_html('<span class="tsa-soft-badge gray">{}</span>', _vi(r"\u0110ang kh\u00f3a"))

    account_status.short_description = _vi(r"T\u00e0i kho\u1ea3n")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description', 'has_video', 'created_at')
    search_fields = ('title', 'description', 'content', 'video_url')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        (_vi(r"Th\u00f4ng tin b\u00e0i h\u1ecdc"), {
            'fields': ('title', 'description')
        }),
        (_vi(r"N\u1ed9i dung b\u00e0i h\u1ecdc"), {
            'fields': ('content', 'video_url')
        }),
        (_vi(r"Th\u1eddi gian"), {
            'fields': ('created_at',)
        }),
    )

    def short_description(self, obj):
        text = obj.description or ''
        return text[:70] + '...' if len(text) > 70 else text or _vi(r"Ch\u01b0a c\u00f3 m\u00f4 t\u1ea3")

    short_description.short_description = _vi(r"M\u00f4 t\u1ea3")

    def has_video(self, obj):
        if obj.video_url:
            return format_html('<span class="tsa-soft-badge green">{}</span>', _vi(r"C\u00f3 video"))
        return format_html('<span class="tsa-soft-badge gray">{}</span>', _vi(r"Ch\u01b0a c\u00f3"))

    has_video.short_description = "Video"


@admin.register(ListeningQuestion)
class ListeningQuestionAdmin(admin.ModelAdmin):
    list_display = ('part_badge', 'question_number', 'short_question', 'correct_answer_badge', 'has_audio', 'created_at')
    list_filter = ('part', 'correct_answer', 'created_at')
    search_fields = ('question_text', 'option_a', 'option_b', 'option_c', 'audio_url', 'audio_file')
    ordering = ('part', 'question_number')
    readonly_fields = ('created_at',)
    list_per_page = 30

    fieldsets = (
        (_vi(r"Th\u00f4ng tin c\u00e2u h\u1ecfi"), {
            'fields': ('part', 'question_number', 'question_text')
        }),
        (_vi(r"\u00c2m thanh"), {
            'fields': ('audio_file', 'audio_url')
        }),
        (_vi(r"C\u00e1c \u0111\u00e1p \u00e1n"), {
            'fields': ('option_a', 'option_b', 'option_c', 'correct_answer')
        }),
        (_vi(r"Th\u1eddi gian"), {
            'fields': ('created_at',)
        }),
    )

    def part_badge(self, obj):
        return format_html('<span class="tsa-soft-badge red">Part {}</span>', obj.part)

    part_badge.short_description = _vi(r"Ph\u1ea7n")

    def short_question(self, obj):
        text = obj.question_text or ''
        return text[:90] + '...' if len(text) > 90 else text

    short_question.short_description = _vi(r"C\u00e2u h\u1ecfi")

    def correct_answer_badge(self, obj):
        return format_html('<span class="tsa-answer-badge">{}</span>', obj.correct_answer)

    correct_answer_badge.short_description = _vi(r"\u0110\u00e1p \u00e1n \u0111\u00fang")

    def has_audio(self, obj):
        if obj.audio_url:
            return format_html('<span class="tsa-soft-badge green">{}</span>', _vi(r"C\u00f3 audio"))
        return format_html('<span class="tsa-soft-badge gray">{}</span>', _vi(r"Ch\u01b0a c\u00f3"))

    has_audio.short_description = "Audio"


@admin.register(HomeBackground)
class HomeBackgroundAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'active_badge', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'image')
    readonly_fields = ('created_at', 'image_preview_large')
    ordering = ('-created_at',)
    list_per_page = 20

    fieldsets = (
        (_vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7"), {
            'fields': ('title', 'image', 'image_preview_large')
        }),
        (_vi(r"Tr\u1ea1ng th\u00e1i s\u1eed d\u1ee5ng"), {
            'fields': ('is_active',)
        }),
        (_vi(r"Th\u1eddi gian"), {
            'fields': ('created_at',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            HomeBackground.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="tsa-thumb" />', obj.image.url)
        return _vi(r"Ch\u01b0a c\u00f3 \u1ea3nh")

    image_preview.short_description = _vi(r"Xem nhanh")

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="tsa-preview-large" />', obj.image.url)
        return _vi(r"Ch\u01b0a c\u00f3 \u1ea3nh")

    image_preview_large.short_description = _vi(r"\u1ea2nh hi\u1ec7n t\u1ea1i")

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="tsa-soft-badge green">{}</span>', _vi(r"\u0110ang hi\u1ec3n th\u1ecb"))
        return format_html('<span class="tsa-soft-badge gray">{}</span>', _vi(r"Kh\u00f4ng s\u1eed d\u1ee5ng"))

    active_badge.short_description = _vi(r"Tr\u1ea1ng th\u00e1i")
