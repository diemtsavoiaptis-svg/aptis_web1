from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from .models import ListeningQuestion


def pick_value(obj, *names, default=""):
    for name in names:
        value = getattr(obj, name, None)
        if value not in [None, ""]:
            return value
    return default


@login_required
def listening_page(request):
    try:
        part_number = int(request.GET.get("part", 1))
    except Exception:
        part_number = 1

    try:
        current_index = int(request.GET.get("q", 1))
    except Exception:
        current_index = 1

    if part_number not in [1, 2, 3, 4]:
        part_number = 1

    questions = ListeningQuestion.objects.filter(part=part_number).order_by("question_number", "id")
    total_questions = questions.count()

    if total_questions == 0:
        return render(request, "core/listening.html", {
            "part_number": part_number,
            "part_tabs": [1, 2, 3, 4],
            "no_question": True,
            "total_questions": 0,
            "all_question_numbers": [],
        })

    if current_index < 1:
        current_index = 1
    if current_index > total_questions:
        current_index = total_questions

    current = questions[current_index - 1]

    question_text = pick_value(current, "question_text", "question", "title", default=f"Câu hỏi {current_index}")
    option_a = pick_value(current, "option_a", "answer_a", "choice_a", default="Đáp án A")
    option_b = pick_value(current, "option_b", "answer_b", "choice_b", default="Đáp án B")
    option_c = pick_value(current, "option_c", "answer_c", "choice_c", default="Đáp án C")
    correct_answer = pick_value(current, "correct_answer", "correct_option", "answer_key", default="A")
    transcript = pick_value(
        current,
        "listening_transcript",
        "transcript",
        "script_text",
        "listening_text",
        "explanation",
        "answer_explanation",
        default="Chưa có transcript.",
    )

    context = {
        "part_number": part_number,
        "part_tabs": [1, 2, 3, 4],
        "question": {
            "id": current.id,
            "prompt": question_text,
            "option_a": option_a,
            "option_b": option_b,
            "option_c": option_c,
            "correct_answer": str(correct_answer).strip().upper(),
            "transcript": transcript,
        },
        "audio_url": reverse("secure_audio", args=[current.id]),
        "current_index": current_index,
        "total_questions": total_questions,
        "progress_percent": round((current_index / total_questions) * 100, 2),
        "prev_url": f"{reverse('listening')}?part={part_number}&q={current_index - 1}" if current_index > 1 else "",
        "next_url": f"{reverse('listening')}?part={part_number}&q={current_index + 1}" if current_index < total_questions else "",
        "all_question_numbers": list(range(1, total_questions + 1)),
    }
    return render(request, "core/listening.html", context)
