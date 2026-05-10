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
        })

    if current_index < 1:
        current_index = 1

    if current_index > total_questions:
        current_index = total_questions

    current = questions[current_index - 1]

    question_text = pick_value(current, "question_text", "question", "title", default="Ch?a c? c?u h?i")
    option_a = pick_value(current, "option_a", "answer_a", "choice_a", default="??p ?n A")
    option_b = pick_value(current, "option_b", "answer_b", "choice_b", default="??p ?n B")
    option_c = pick_value(current, "option_c", "answer_c", "choice_c", default="??p ?n C")
    correct_answer = pick_value(current, "correct_answer", "correct_option", "answer_key", default="A")
    transcript = pick_value(
        current,
        "listening_transcript",
        "transcript",
        "script_text",
        "listening_text",
        "explanation",
        "answer_explanation",
        default="Ch?a c? n?i dung nghe / gi?i th?ch.",
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
        "jump_numbers": list(range(max(1, current_index - 3), min(total_questions, current_index + 3) + 1)),
    }

    return render(request, "core/listening.html", context)
