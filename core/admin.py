from django.utils.html import format_html as django_format_html
from django.contrib import admin
from django.utils.safestring import mark_safe
from .drive_audio import extract_drive_file_id

from .forms import ListeningQuestionAdminForm
from .models import StudentProfile, Lesson, ListeningQuestion, HomeBackground, UserDeviceSession, SecurityAlert, Part2Topic, Part2Voice, SiteBackground, LoginThumbnail
from .supabase_storage import build_audio_key, upload_file_to_supabase


def _vi(text):
    return text.encode("ascii").decode("unicode_escape")


admin.site.site_header = _vi(r"Qu\u1ea3n tr\u1ecb TSA Aptis")
admin.site.site_title = _vi(r"Qu\u1ea3n tr\u1ecb TSA Aptis")
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
            return format_html('<span class="tsa-red-alert">{} cảnh báo</span>', count)
        return format_html('<span class="tsa-soft-badge green">Bình thường</span>')

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
    list_display = (
        "question_number",
        "drive_audio_column",
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "correct_answer",
        "listening_transcript",
    )

    list_display_links = ("question_number",)

    list_editable = (
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "correct_answer",
        "listening_transcript",
    )

    list_filter = ()
    search_fields = (
        "question_text",
        "listening_transcript",
        "option_a",
        "option_b",
        "option_c",
        "audio_drive_link",
        "audio_drive_file_id",
        "audio_file_name",
    )

    ordering = ("part", "question_number")
    list_per_page = 200
    readonly_fields = ("created_at", "audio_drive_file_id")
    save_on_top = True

    fieldsets = (
        (_vi(r"Th\u00f4ng tin c\u00e2u h\u1ecfi"), {
            "fields": ("part", "question_number", "question_text")
        }),
        (_vi(r"File nghe Google Drive"), {
            "fields": ("audio_drive_link", "audio_drive_file_id"),
            "description": _vi(r"D\u00e1n link Google Drive MP3 v\u00e0o \u00f4 Link Google Drive MP3.")
        }),
        (_vi(r"Audio d\u1ef1 ph\u00f2ng"), {
            "fields": ("audio_file", "audio_url")
        }),
        (_vi(r"Ba c\u00e2u tr\u1ea3 l\u1eddi v\u00e0 \u0111\u00e1p \u00e1n \u0111\u00fang"), {
            "fields": ("option_a", "option_b", "option_c", "correct_answer")
        }),
        (_vi(r"\u0110\u1ec1 b\u00e0i nghe hi\u1ec3n th\u1ecb sau khi ki\u1ec3m tra \u0111\u00e1p \u00e1n"), {
            "fields": ("listening_transcript",)
        }),
        (_vi(r"Th\u1eddi gian"), {
            "fields": ("created_at",)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.audio_drive_link:
            obj.audio_drive_file_id = extract_drive_file_id(obj.audio_drive_link)
        super().save_model(request, obj, form, change)

    def drive_audio_column(self, obj):
        if obj.audio_drive_file_id:
            return format_html(
                '<span class="tsa-soft-badge green">Drive</span><br><small>{}</small>',
                obj.audio_file_name or obj.audio_drive_file_id
            )
        if obj.audio_file:
            return mark_safe('<span class="tsa-soft-badge green">File local</span>')
        if obj.audio_url:
            return mark_safe('<span class="tsa-orange-alert">Link ngoài</span>')
        return mark_safe('<span class="tsa-soft-badge gray">Chưa có audio</span>')

    drive_audio_column.short_description = "File nghe"

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


@admin.action(description="Đánh dấu đã xử lý")
def mark_alert_resolved(modeladmin, request, queryset):
    queryset.update(is_resolved=True)


@admin.action(description="Đánh dấu chưa xử lý")
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
        ("Thông tin cảnh báo", {"fields": ("user", "severity", "reason", "is_resolved")}),
        ("Dấu hiệu đăng nhập", {"fields": ("ip_address", "user_agent")}),
        ("Thời gian", {"fields": ("created_at", "updated_at")}),
    )

    def red_alert(self, obj):
        if obj.severity == "critical":
            return format_html('<span class="tsa-red-alert">BÁO ĐỘNG ĐỎ</span>')
        if obj.severity == "high":
            return mark_safe('<span class="tsa-orange-alert">CẢNH BÁO CAO</span>')
        if obj.severity == "medium":
            return mark_safe('<span class="tsa-yellow-alert">CẢNH BÁO</span>')
        return mark_safe('<span class="tsa-soft-badge gray">Theo dõi</span>')

    red_alert.short_description = "Mức cảnh báo"

    def resolved_badge(self, obj):
        if obj.is_resolved:
            return mark_safe('<span class="tsa-soft-badge green">Đã xử lý</span>')
        return mark_safe('<span class="tsa-red-alert">Chưa xử lý</span>')

    resolved_badge.short_description = "Trạng thái"

    def short_user_agent(self, obj):
        text = obj.user_agent or ""
        return text[:90] + "..." if len(text) > 90 else text

    short_user_agent.short_description = "Thiết bị / trình duyệt"


# Auto-register các model chưa hiện trong admin
from django.apps import apps
from django.contrib import admin

# SAFE_FORMAT_HTML_START
def format_html(format_string, *args, **kwargs):
    """
    Django 6 không cho format_html('<span>html tĩnh</span>') nếu không truyền args.
    Hàm này giữ code admin cũ chạy ổn:
    - Có args/kwargs: dùng format_html gốc của Django.
    - Không có args/kwargs: dùng mark_safe cho HTML tĩnh.
    """
    if not args and not kwargs:
        return mark_safe(format_string)
    return django_format_html(format_string, *args, **kwargs)
# SAFE_FORMAT_HTML_END

for model in apps.get_app_config("core").get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass


# ===== Admin Part 2 =====
from django.contrib.admin.sites import NotRegistered

try:
    admin.site.unregister(Part2Topic)
except NotRegistered:
    pass

try:
    admin.site.unregister(Part2Voice)
except NotRegistered:
    pass


class Part2VoiceInline(admin.TabularInline):
    model = Part2Voice
    extra = 4
    fields = (
        "order",
        "audio_url",
        "answer_a",
        "answer_b",
        "answer_c",
        "answer_d",
        "transcript",
        "data_choices",
        "correct_answer",
    )


@admin.register(Part2Topic)
class Part2TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title", "description")
    inlines = [Part2VoiceInline]


@admin.register(Part2Voice)
class Part2VoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "order", "correct_answer")
    list_filter = ("topic", "correct_answer")
    search_fields = ("topic__title", "transcript", "data_choices")
# ===== End Admin Part 2 =====







# ===== Safe admin register for interface images =====
from django.contrib.admin.sites import NotRegistered

for _model in [SiteBackground, LoginThumbnail]:
    try:
        admin.site.unregister(_model)
    except NotRegistered:
        pass


@admin.register(SiteBackground)
class SiteBackgroundAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "image_url")



# ===== End safe admin register for interface images =====


# ===== Safe LoginThumbnail admin register =====
from django.contrib.admin.sites import NotRegistered

try:
    admin.site.unregister(LoginThumbnail)
except NotRegistered:
    pass


@admin.register(LoginThumbnail)
class LoginThumbnailAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = (
        "name",
        "image_url",
        "ticker_text_1",
        "ticker_text_2",
        "ticker_text_3",
        "ticker_text_4",
        "ticker_text_5",
    )
# ===== End Safe LoginThumbnail admin register =====
