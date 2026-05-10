from django.contrib import admin
from django.utils.html import format_html

from .forms import ListeningQuestionAdminForm
from .models import StudentProfile, Lesson, ListeningQuestion, HomeBackground, UserDeviceSession, SecurityAlert
from .supabase_storage import build_audio_key, upload_file_to_supabase


def _vi(text):
    return text.encode("ascii").decode("unicode_escape")


admin.site.site_header = _vi(r"Qu\u1ea3n tr\u1ecb TSA Aptis")
admin.site.site_title = "TSA Aptis Admin"
admin.site.index_title = _vi(r"Site qu\u1ea3n tr\u1ecb h\u1ec7 th\u1ed1ng")


@admin.action(description=_vi(r"Duy\u1ec7t h\u1ecdc vi\u00ean \u0111\u00e3 ch\u1ecdn"))
def approve_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = "approved"
        student.save()
        student.user.is_active = True
        student.user.save()


@admin.action(description=_vi(r"T\u1eeb ch\u1ed1i h\u1ecdc vi\u00ean \u0111\u00e3 ch\u1ecdn"))
def reject_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = "rejected"
        student.save()
        student.user.is_active = False
        student.user.save()


@admin.action(description=_vi(r"\u0110\u01b0a h\u1ecdc vi\u00ean v\u1ec1 tr\u1ea1ng th\u00e1i ch\u1edd duy\u1ec7t"))
def pending_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = "pending"
        student.save()
        student.user.is_active = False
        student.user.save()


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "status_badge", "account_status", "security_count", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone", "user__username")
    actions = [approve_students, reject_students, pending_students]
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (_vi(r"Th\u00f4ng tin h\u1ecdc vi\u00ean"), {"fields": ("user", "full_name", "email", "phone")}),
        (_vi(r"Tr\u1ea1ng th\u00e1i x\u00e9t duy\u1ec7t"), {"fields": ("status", "created_at")}),
    )

    def status_badge(self, obj):
        colors = {"pending": "#f59e0b", "approved": "#12a150", "rejected": "#d40000"}
        labels = {"pending": _vi(r"Ch\u1edd duy\u1ec7t"), "approved": _vi(r"\u0110\u00e3 duy\u1ec7t"), "rejected": _vi(r"T\u1eeb ch\u1ed1i")}
        return format_html('<span class="tsa-badge" style="background:{};">{}</span>', colors.get(obj.status, "#555"), labels.get(obj.status, obj.status))

    status_badge.short_description = _vi(r"Tr\u1ea1ng th\u00e1i")

    def account_status(self, obj):
        if obj.user.is_active:
            return format_html('<span class="tsa-soft-badge green">{}</span>', _vi(r"\u0110ang ho\u1ea1t \u0111\u1ed9ng"))
        return format_html('<span class="tsa-soft-badge gray">{}</span>', _vi(r"\u0110ang kh\u00f3a"))

    account_status.short_description = _vi(r"T\u00e0i kho\u1ea3n")

    def security_count(self, obj):
        count = obj.user.security_alerts.filter(is_resolved=False).count()
        if count:
            return format_html('<span class="tsa-red-alert">{} c?nh b?o</span>', count)
        return format_html('<span class="tsa-soft-badge green">B?nh th??ng</span>')

    security_count.short_description = _vi(r"B\u1ea3o m\u1eadt")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "short_description", "has_video", "created_at")
    search_fields = ("title", "description", "content", "video_url")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (_vi(r"Th\u00f4ng tin b\u00e0i h\u1ecdc"), {"fields": ("title", "description")}),
        (_vi(r"N\u1ed9i dung b\u00e0i h\u1ecdc"), {"fields": ("content", "video_url")}),
        (_vi(r"Th\u1eddi gian"), {"fields": ("created_at",)}),
    )

    def short_description(self, obj):
        text = obj.description or ""
        return text[:70] + "..." if len(text) > 70 else text or _vi(r"Ch\u01b0a c\u00f3 m\u00f4 t\u1ea3")

    short_description.short_description = _vi(r"M\u00f4 t\u1ea3")

    def has_video(self, obj):
        if obj.video_url:
            return format_html('<span class="tsa-soft-badge green">{}</span>', _vi(r"C\u00f3 video"))
        return format_html('<span class="tsa-soft-badge gray">{}</span>', _vi(r"Ch\u01b0a c\u00f3"))

    has_video.short_description = "Video"


@admin.register(ListeningQuestion)
class ListeningQuestionAdmin(admin.ModelAdmin):
    form = ListeningQuestionAdminForm

    list_display = (
        "part_badge",
        "question_number",
        "audio_column",
        "question_column",
        "answers_column",
        "correct_answer_badge",
        "transcript_status",
        "supabase_audio_status",
        "created_at",
    )

    list_filter = ("part", "correct_answer", "audio_provider", "created_at")
    search_fields = (
        "question_text",
        "listening_transcript",
        "option_a",
        "option_b",
        "option_c",
        "audio_url",
        "audio_key",
        "audio_file_name",
    )
    ordering = ("part", "question_number")
    readonly_fields = (
        "created_at",
        "audio_provider",
        "audio_key",
        "audio_file_name",
        "audio_size",
        "audio_content_type",
    )
    list_per_page = 30

    fieldsets = (
        (_vi(r"Th\u00f4ng tin c\u00e2u h\u1ecfi"), {
            "fields": ("part", "question_number", "question_text")
        }),
        (_vi(r"File nghe MP3"), {
            "fields": ("upload_audio_mp3", "audio_provider", "audio_key", "audio_file_name", "audio_size", "audio_content_type")
        }),
        (_vi(r"Audio d\u1ef1 ph\u00f2ng"), {
            "fields": ("audio_file", "audio_url")
        }),
        (_vi(r"Ba c\u00e2u tr\u1ea3 l\u1eddi v\u00e0 \u0111\u00e1p \u00e1n \u0111\u00fang"), {
            "fields": ("option_a", "option_b", "option_c", "correct_answer")
        }),
        (_vi(r"\u0110\u1ec1 b\u00e0i nghe hi\u1ec3n th\u1ecb sau khi ki\u1ec3m tra \u0111\u00e1p \u00e1n"), {
            "fields": ("listening_transcript",),
            "description": _vi(r"N\u1ed9i dung n\u00e0y ch\u1ec9 hi\u1ec3n cho h\u1ecdc vi\u00ean sau khi b\u1ea5m n\u1ed9p b\u00e0i / ki\u1ec3m tra \u0111\u00e1p \u00e1n.")
        }),
        (_vi(r"Th\u1eddi gian"), {
            "fields": ("created_at",)
        }),
    )

    def save_model(self, request, obj, form, change):
        upload_file = form.cleaned_data.get("upload_audio_mp3")

        if upload_file:
            key = build_audio_key(obj, upload_file.name)
            result = upload_file_to_supabase(upload_file, key)

            obj.audio_provider = "supabase"
            obj.audio_key = result["key"]
            obj.audio_file_name = upload_file.name
            obj.audio_size = result["size"]
            obj.audio_content_type = result["content_type"]

        super().save_model(request, obj, form, change)

    def part_badge(self, obj):
        return format_html('<span class="tsa-soft-badge red">Part {}</span>', obj.part)

    part_badge.short_description = _vi(r"Ph\u1ea7n")

    def audio_column(self, obj):
        if obj.audio_provider == "supabase" and obj.audio_key:
            return format_html('<span class="tsa-soft-badge green">MP3 Supabase</span><br><small>{}</small>', obj.audio_file_name or "?? upload")
        if obj.audio_file:
            return format_html('<span class="tsa-soft-badge green">MP3 local</span>')
        if obj.audio_url:
            return format_html('<span class="tsa-orange-alert">Link ngo?i</span>')
        return format_html('<span class="tsa-soft-badge gray">Ch?a c? file</span>')

    audio_column.short_description = "File nghe"

    def question_column(self, obj):
        text = obj.question_text or ""
        if len(text) > 90:
            text = text[:90] + "..."
        return text

    question_column.short_description = _vi(r"C\u00e2u h\u1ecfi")

    def answers_column(self, obj):
        return format_html(
            "<div><b>A.</b> {}</div><div><b>B.</b> {}</div><div><b>C.</b> {}</div>",
            obj.option_a,
            obj.option_b,
            obj.option_c,
        )

    answers_column.short_description = _vi(r"Ba c\u00e2u tr\u1ea3 l\u1eddi")

    def correct_answer_badge(self, obj):
        return format_html('<span class="tsa-answer-badge">{}</span>', obj.correct_answer)

    correct_answer_badge.short_description = _vi(r"\u0110\u00e1p \u00e1n \u0111\u00fang")

    def transcript_status(self, obj):
        if obj.listening_transcript:
            return format_html('<span class="tsa-soft-badge green">C? ?? b?i nghe</span>')
        return format_html('<span class="tsa-soft-badge gray">Ch?a nh?p</span>')

    transcript_status.short_description = _vi(r"\u0110\u1ec1 b\u00e0i nghe")

    def supabase_audio_status(self, obj):
        if obj.audio_provider == "supabase" and obj.audio_key:
            return format_html('<span class="tsa-soft-badge green">Supabase</span>')
        if obj.audio_file:
            return format_html('<span class="tsa-soft-badge green">File local</span>')
        if obj.audio_url:
            return format_html('<span class="tsa-orange-alert">Link ngo?i</span>')
        return format_html('<span class="tsa-soft-badge gray">Ch?a c?</span>')

    supabase_audio_status.short_description = "Kho l?u"

@admin.register(HomeBackground)
class HomeBackgroundAdmin(admin.ModelAdmin):
    list_display = ("title", "image_preview", "active_badge", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "image")
    readonly_fields = ("created_at", "image_preview_large")
    ordering = ("-created_at",)
    list_per_page = 20

    fieldsets = (
        (_vi(r"\u1ea2nh n\u1ec1n trang ch\u1ee7"), {"fields": ("title", "image", "image_preview_large")}),
        (_vi(r"Tr\u1ea1ng th\u00e1i s\u1eed d\u1ee5ng"), {"fields": ("is_active",)}),
        (_vi(r"Th\u1eddi gian"), {"fields": ("created_at",)}),
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


@admin.register(UserDeviceSession)
class UserDeviceSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "short_device", "created_at", "last_seen")
    search_fields = ("user__username", "user__email", "ip_address", "user_agent", "device_id", "session_key")
    list_filter = ("created_at", "last_seen")
    readonly_fields = ("user", "session_key", "device_id", "user_agent", "ip_address", "created_at", "last_seen")
    ordering = ("-last_seen",)
    list_per_page = 30

    def short_device(self, obj):
        text = obj.user_agent or ""
        return text[:90] + "..." if len(text) > 90 else text

    short_device.short_description = _vi(r"Thi\u1ebft b\u1ecb / tr\u00ecnh duy\u1ec7t")


@admin.action(description="??nh d?u ?? x? l?")
def mark_alert_resolved(modeladmin, request, queryset):
    queryset.update(is_resolved=True)


@admin.action(description="??nh d?u ch?a x? l?")
def mark_alert_unresolved(modeladmin, request, queryset):
    queryset.update(is_resolved=False)


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ("red_alert", "user", "reason", "ip_address", "short_user_agent", "resolved_badge", "created_at")
    list_filter = ("severity", "is_resolved", "created_at")
    search_fields = ("user__username", "user__email", "reason", "ip_address", "user_agent")
    readonly_fields = ("user", "severity", "reason", "ip_address", "user_agent", "created_at", "updated_at")
    actions = [mark_alert_resolved, mark_alert_unresolved]
    ordering = ("is_resolved", "-created_at")
    list_per_page = 30

    fieldsets = (
        ("Th?ng tin c?nh b?o", {"fields": ("user", "severity", "reason", "is_resolved")}),
        ("D?u hi?u ??ng nh?p", {"fields": ("ip_address", "user_agent")}),
        ("Th?i gian", {"fields": ("created_at", "updated_at")}),
    )

    def red_alert(self, obj):
        if obj.severity == "critical":
            return format_html('<span class="tsa-red-alert">B?O ??NG ??</span>')
        if obj.severity == "high":
            return format_html('<span class="tsa-orange-alert">C?NH B?O CAO</span>')
        if obj.severity == "medium":
            return format_html('<span class="tsa-yellow-alert">C?NH B?O</span>')
        return format_html('<span class="tsa-soft-badge gray">Theo d?i</span>')

    red_alert.short_description = "M?c c?nh b?o"

    def resolved_badge(self, obj):
        if obj.is_resolved:
            return format_html('<span class="tsa-soft-badge green">?? x? l?</span>')
        return format_html('<span class="tsa-red-alert">Ch?a x? l?</span>')

    resolved_badge.short_description = "Tr?ng th?i"

    def short_user_agent(self, obj):
        text = obj.user_agent or ""
        return text[:90] + "..." if len(text) > 90 else text

    short_user_agent.short_description = "Thi?t b? / tr?nh duy?t"
