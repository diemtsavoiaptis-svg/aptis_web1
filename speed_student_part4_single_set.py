from pathlib import Path

views_path = Path("core/views.py")
text = views_path.read_text(encoding="utf-8-sig")

start = text.find("def student_part4_page(request):")
if start == -1:
    raise SystemExit("Cannot find student_part4_page in core/views.py")

next_def = text.find("\ndef ", start + 1)
if next_def == -1:
    next_def = len(text)

new_func = r'''@login_required
def student_part4_page(request):
    try:
        current_index = int(request.GET.get("set", 1))
    except ValueError:
        current_index = 1

    materials_qs = (
        ListeningPartMaterial.objects
        .filter(part=4)
        .only("id", "title", "description", "audio_url", "transcript")
        .order_by("id")
    )

    total_sets = materials_qs.count()

    if total_sets == 0:
        return render(request, "core/student_part4.html", {
            "selected": None,
            "questions": [],
            "current_index": 0,
            "total_sets": 0,
            "progress_percent": 0,
            "prev_url": None,
            "next_url": None,
            "student_watermark": f"{request.user.username} · {request.user.email}",
        })

    if current_index < 1:
        current_index = 1

    if current_index > total_sets:
        current_index = total_sets

    selected = materials_qs[current_index - 1]

    questions = list(
        ListeningPartQuestion.objects
        .filter(material=selected)
        .only(
            "id",
            "material_id",
            "order",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "option_e",
            "option_f",
            "correct_answer",
        )
        .order_by("order", "id")
    )

    progress_percent = int((current_index / total_sets) * 100) if total_sets else 0

    prev_url = None
    next_url = None

    if current_index > 1:
        prev_url = f"{request.path}?set={current_index - 1}"

    if current_index < total_sets:
        next_url = f"{request.path}?set={current_index + 1}"

    response = render(request, "core/student_part4.html", {
        "selected": selected,
        "questions": questions,
        "current_index": current_index,
        "total_sets": total_sets,
        "progress_percent": progress_percent,
        "prev_url": prev_url,
        "next_url": next_url,
        "student_watermark": f"{request.user.username} · {request.user.email}",
    })

    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"

    return response

'''

text = text[:start] + new_func + text[next_def:]
views_path.write_text(text, encoding="utf-8")

print("Done: Student Part 4 now loads only the current set.")
