from pathlib import Path
import re

views_path = Path("core/views.py")
text = views_path.read_text(encoding="utf-8-sig")

if "import random" not in text:
    text = text.replace("import requests\n", "import requests\nimport random\n")

if "import json" not in text:
    text = text.replace("import requests\n", "import requests\nimport json\n")

if "from django.utils import timezone" not in text:
    text = text.replace("from django.views.decorators.http import require_POST\n", "from django.views.decorators.http import require_POST\nfrom django.utils import timezone\n")

if "from pathlib import Path" not in text:
    text = text.replace("import requests\n", "import requests\nfrom pathlib import Path\n")

if "from django.conf import settings" not in text:
    text = text.replace("from django.shortcuts import render, get_object_or_404\n", "from django.shortcuts import render, get_object_or_404\nfrom django.conf import settings\n")

if "from django.db import transaction" not in text:
    text = text.replace("from django.db.models import Q\n", "from django.db.models import Q\nfrom django.db import transaction\n")

safe_shuffle_block = '''        if action == "shuffle_all":
            questions_to_shuffle = list(
                ListeningQuestion.objects.filter(
                    part=1,
                    question_number__gte=1,
                    question_number__lte=191,
                ).order_by("question_number", "id")
            )

            if len(questions_to_shuffle) != 191:
                messages.error(
                    request,
                    f"Shuffle cancelled. Expected exactly 191 Part 1 rows, found {len(questions_to_shuffle)}."
                )
                return redirect("admin_part1_questions")

            numbers = [q.question_number for q in questions_to_shuffle]
            if numbers != list(range(1, 192)):
                messages.error(
                    request,
                    "Shuffle cancelled. Part 1 question numbers must be exactly 1 to 191 before shuffling."
                )
                return redirect("admin_part1_questions")

            backup_dir = Path(settings.BASE_DIR) / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"part1_locked_before_shuffle_{timestamp}.json"

            backup_payload = []
            for q in questions_to_shuffle:
                backup_payload.append({
                    "id": q.id,
                    "part": q.part,
                    "question_number": q.question_number,
                    "question_text": q.question_text,
                    "listening_transcript": q.listening_transcript,
                    "audio_url": q.audio_url,
                    "audio_drive_link": getattr(q, "audio_drive_link", ""),
                    "audio_drive_file_id": getattr(q, "audio_drive_file_id", ""),
                    "audio_file": q.audio_file.name if getattr(q, "audio_file", None) else "",
                    "audio_provider": getattr(q, "audio_provider", ""),
                    "audio_key": getattr(q, "audio_key", ""),
                    "audio_file_name": getattr(q, "audio_file_name", ""),
                    "audio_size": getattr(q, "audio_size", 0),
                    "audio_content_type": getattr(q, "audio_content_type", ""),
                    "voice_info": getattr(q, "voice_info", ""),
                    "voice_info_locked": getattr(q, "voice_info_locked", False),
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "correct_answer": q.correct_answer,
                })

            backup_path.write_text(
                json.dumps(backup_payload, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            payloads = []
            for q in questions_to_shuffle:
                payloads.append({
                    "question_text": q.question_text,
                    "listening_transcript": q.listening_transcript,
                    "audio_url": q.audio_url,
                    "audio_drive_link": getattr(q, "audio_drive_link", ""),
                    "audio_drive_file_id": getattr(q, "audio_drive_file_id", ""),
                    "audio_file": q.audio_file.name if getattr(q, "audio_file", None) else "",
                    "audio_provider": getattr(q, "audio_provider", ""),
                    "audio_key": getattr(q, "audio_key", ""),
                    "audio_file_name": getattr(q, "audio_file_name", ""),
                    "audio_size": getattr(q, "audio_size", 0),
                    "audio_content_type": getattr(q, "audio_content_type", ""),
                    "voice_info": getattr(q, "voice_info", ""),
                    "voice_info_locked": True,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "correct_answer": q.correct_answer,
                })

            random.shuffle(payloads)

            with transaction.atomic():
                for index, q in enumerate(questions_to_shuffle, start=1):
                    data = payloads[index - 1]

                    q.question_number = index
                    q.question_text = data["question_text"]
                    q.listening_transcript = data["listening_transcript"]
                    q.audio_url = data["audio_url"]
                    q.audio_drive_link = data["audio_drive_link"]
                    q.audio_drive_file_id = data["audio_drive_file_id"]
                    q.audio_file.name = data["audio_file"]
                    q.audio_provider = data["audio_provider"]
                    q.audio_key = data["audio_key"]
                    q.audio_file_name = data["audio_file_name"]
                    q.audio_size = data["audio_size"]
                    q.audio_content_type = data["audio_content_type"]
                    q.voice_info = data["voice_info"]
                    q.voice_info_locked = True
                    q.option_a = data["option_a"]
                    q.option_b = data["option_b"]
                    q.option_c = data["option_c"]
                    q.correct_answer = data["correct_answer"]
                    q.save()

            messages.success(
                request,
                f"Locked backup created, then shuffled exactly 191 Part 1 rows. Backup file: {backup_path.name}"
            )
            return redirect("admin_part1_questions")

'''

pattern = r'        if action == "shuffle_all":\n.*?        if action == "save_all":'
replacement = safe_shuffle_block + '        if action == "save_all":'

if 'if action == "shuffle_all":' in text:
    text = re.sub(pattern, replacement, text, flags=re.S)
else:
    marker = '        if action == "save_all":'
    text = text.replace(marker, safe_shuffle_block + marker)

views_path.write_text(text, encoding="utf-8")

print("Done: Part 1 shuffle is now locked, backed up, and limited to exactly 191 rows.")
