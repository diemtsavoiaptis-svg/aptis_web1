from pathlib import Path
import re

views_path = Path("core/views.py")
views = views_path.read_text(encoding="utf-8", errors="ignore")

# Delete bản lỗi/thiếu nếu có rồi thêm lại cuối file
views = re.sub(
    r'\n@login_required\s+def admin_listening_parts\(request\):.*?(?=\n@login_required\s+def|\Z)',
    "\n",
    views,
    flags=re.S
)
views = re.sub(
    r'\n@login_required\s+def admin_part1_questions\(request\):.*?(?=\n@login_required\s+def|\Z)',
    "\n",
    views,
    flags=re.S
)

views += r'''

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
                    question_text=f"Question {current_max + i}",
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
                q.correct_answer = request.POST.get(f"correct_answer_{row_id}", "A").strip().upper()[:1] or "A"
                q.listening_transcript = request.POST.get(f"listening_transcript_{row_id}", "").strip()

                if hasattr(q, "audio_drive_link"):
                    q.audio_drive_link = request.POST.get(f"audio_drive_link_{row_id}", "").strip()

                if hasattr(q, "audio_url"):
                    q.audio_url = request.POST.get(f"audio_url_{row_id}", "").strip()

                q.save()

            messages.success(request, "Đã cập nhật hàng loạt questions Part 1.")
            return redirect("admin_part1_questions")

        if action == "delete_one":
            delete_id = request.POST.get("delete_id")
            ListeningQuestion.objects.filter(id=delete_id, part=1).delete()
            messages.success(request, "Đã xóa 1 questions Part 1.")
            return redirect("admin_part1_questions")

    questions = ListeningQuestion.objects.filter(part=1).order_by("question_number", "id")

    return render(request, "core/admin_part1_questions.html", {
        "questions": questions,
        "total_questions": questions.count(),
    })
'''

views_path.write_text(views, encoding="utf-8")
print("DA_THEM_LAI_ADMIN_LISTENING_PARTS_VA_PART1")


# Edit urls.py cho chắc, không để trùng quá nhiều
urls_path = Path("core/urls.py")
urls = urls_path.read_text(encoding="utf-8", errors="ignore")

urls = re.sub(
    r'\s*path\("dashboard/listening-parts/".*?admin_listening_parts.*?\),\n?',
    "",
    urls
)
urls = re.sub(
    r'\s*path\("dashboard/part-1/".*?admin_part1_questions.*?\),\n?',
    "",
    urls
)

urls = urls.replace(
    'path("dashboard/", views.dashboard, name="dashboard"),',
    'path("dashboard/", views.dashboard, name="dashboard"),\n    path("dashboard/listening-parts/", views.admin_listening_parts, name="admin_listening_parts"),\n    path("dashboard/part-1/", views.admin_part1_questions, name="admin_part1_questions"),'
)

urls_path.write_text(urls, encoding="utf-8")
print("DA_SUA_LAI_CORE_URLS")
