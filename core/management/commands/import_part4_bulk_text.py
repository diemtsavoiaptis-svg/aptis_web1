from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import ListeningPartMaterial, ListeningPartQuestion


class Command(BaseCommand):
    help = "Bulk import Listening Part 4 text data from pasted table."

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Listening Part 4 Bulk Import"))
        self.stdout.write("Please paste your data below. When finished, type END on a new line.")
        self.stdout.write("")
        self.stdout.write("Expected columns:")
        self.stdout.write("question | topic | question_16 | q16_answer_1 | q16_answer_2 | q16_answer_3 | question_17 | q17_answer_1 | q17_answer_2 | q17_answer_3 | paraphrase")
        self.stdout.write("")

        lines = []

        while True:
            try:
                line = input()
            except EOFError:
                break

            if line.strip() == "END":
                break

            if line.strip():
                lines.append(line.rstrip("\n"))

        if not lines:
            raise CommandError("No data pasted.")

        created = 0
        skipped = 0

        with transaction.atomic():
            for line_number, line in enumerate(lines, start=1):
                parts = self.split_row(line)

                if len(parts) < 11:
                    skipped += 1
                    self.stdout.write(self.style.WARNING(
                        f"Skipped row {line_number}: expected 11 columns, got {len(parts)}."
                    ))
                    continue

                question_label = parts[0].strip()
                topic = parts[1].strip()
                q16_text = parts[2].strip()
                q16_a = parts[3].strip()
                q16_b = parts[4].strip()
                q16_c = parts[5].strip()
                q17_text = parts[6].strip()
                q17_a = parts[7].strip()
                q17_b = parts[8].strip()
                q17_c = parts[9].strip()
                paraphrase = parts[10].strip()

                if self.looks_like_header(question_label, topic, q16_text):
                    skipped += 1
                    continue

                if not any([question_label, topic, q16_text, q17_text, paraphrase]):
                    skipped += 1
                    continue

                material = ListeningPartMaterial.objects.create(
                    part=4,
                    title=topic or "Untitled Topic",
                    description=question_label,
                    instructions="Listen to the audio and choose the correct answer.",
                    audio_url="",
                    transcript=paraphrase,
                    is_active=True,
                )

                ListeningPartQuestion.objects.create(
                    material=material,
                    order=16,
                    question_text=q16_text or "Question 16",
                    option_a=q16_a,
                    option_b=q16_b,
                    option_c=q16_c,
                    option_d="",
                    option_e="",
                    option_f="",
                    correct_answer="A",
                    explanation="",
                )

                ListeningPartQuestion.objects.create(
                    material=material,
                    order=17,
                    question_text=q17_text or "Question 17",
                    option_a=q17_a,
                    option_b=q17_b,
                    option_c=q17_c,
                    option_d="",
                    option_e="",
                    option_f="",
                    correct_answer="A",
                    explanation="",
                )

                created += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import completed."))
        self.stdout.write(f"Created Part 4 rows: {created}")
        self.stdout.write(f"Skipped rows: {skipped}")
        self.stdout.write("")
        self.stdout.write("Next:")
        self.stdout.write("1. Open /dashboard/part-4/")
        self.stdout.write("2. Click the correct answer cells")
        self.stdout.write("3. Add audio links later when MP3 files are ready")
        self.stdout.write("")

    def split_row(self, line):
        if "\t" in line:
            return [x.strip() for x in line.split("\t")]

        if "|" in line:
            return [x.strip() for x in line.split("|")]

        return [x.strip() for x in line.split(",")]

    def looks_like_header(self, question_label, topic, q16_text):
        text = " ".join([question_label, topic, q16_text]).lower()
        return (
            "question" in text
            and "topic" in text
            and (
                "câu hỏi 16" in text
                or "question_16" in text
                or "question 16" in text
                or "q16" in text
            )
        )
