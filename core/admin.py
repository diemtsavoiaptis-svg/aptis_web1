from django.contrib import admin
from .models import StudentProfile, Lesson, ListeningQuestion, HomeBackground


@admin.action(description='Duy?t h?c vi?n ?? ch?n')
def approve_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = 'approved'
        student.save()

        student.user.is_active = True
        student.user.save()


@admin.action(description='T? ch?i h?c vi?n ?? ch?n')
def reject_students(modeladmin, request, queryset):
    for student in queryset:
        student.status = 'rejected'
        student.save()

        student.user.is_active = False
        student.user.save()


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'email')
    actions = [approve_students, reject_students]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(ListeningQuestion)
class ListeningQuestionAdmin(admin.ModelAdmin):
    list_display = ('part', 'question_number', 'question_text', 'correct_answer', 'created_at')
    list_filter = ('part', 'created_at')
    search_fields = ('question_text',)
    ordering = ('part', 'question_number')


@admin.register(HomeBackground)
class HomeBackgroundAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
