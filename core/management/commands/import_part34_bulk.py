from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import ListeningPartMaterial, ListeningPartQuestion


class Command(BaseCommand):
    help = "Import Listening Part 3/4 material and questions from pasted text."

    def add_arguments(self, parser):
        parser.add_argument(
            "--part",
            type=int,
            choices=[3, 4],
            default=3,
            help="Listening part number: 3 or 4."
        )

    def handle(self, *args, **options):
        part = options["part"]

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Import Listening Part {part}"))
        self.stdout.write("Paste your data below. When finished, type END on a new line.")
        self.stdout.write("")
        self.stdout.write("Format:")
        self.stdout.write("TITLE: Topic name")
        self.stdout.write("AUDIO: https://...")
        self.stdout.write("INSTRUCTIONS: Write instructions here")
        self.stdout.write("TRANSCRIPT: Write transcript here")
        self.stdout.write("---")
        self.stdout.write("Q: Question text")
        self.stdout.write("A: Option A")
        self.stdout.write("B: Option B")
        self.stdout.write("C: Option C")
        self.stdout.write("D: Option D")
        self.stdout.write("E: Option E")
        self.stdout.write("F: Option F")
        self.stdout.write("ANSWER: A")
        self.stdout.write("EXPLANATION: Optional explanation")
        self.stdout.write("---")
        self.stdout.write("Q: Next question")
        self.stdout.write("...")
        self.stdout.write("END")
        self.stdout.write("")

        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break

            if line.strip() == "END":
                break

            lines.append(line)

        raw_text = "\n".join(lines).strip()

        if not raw_text:
            raise CommandError("No data pasted.")

        data = self.parse_data(raw_text)

        with transaction.atomic():
            material = ListeningPartMaterial.objects.create(
                part=part,
                title=data["title"],
                description=data.get("description", ""),
                instructions=data.get("instructions", ""),
                audio_url=data.get("audio", ""),
                transcript=data.get("transcript", ""),
                is_active=True,
            )

            created_questions = 0

            for index, item in enumerate(data["questions"], start=1):
                ListeningPartQuestion.objects.create(
                    material=material,
                    order=index,
                    question_text=item.get("question", ""),
                    option_a=item.get("a", ""),
                    option_b=item.get("b", ""),
                    option_c=item.get("c", ""),
                    option_d=item.get("d", ""),
                    option_e=item.get("e", ""),
                    option_f=item.get("f", ""),
                    correct_answer=item.get("answer", "A").upper()[:1] or "A",
                    explanation=item.get("explanation", ""),
                )
                created_questions += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Import completed."))
        self.stdout.write(f"Material ID: {material.id}")
        self.stdout.write(f"Title: {material.title}")
        self.stdout.write(f"Questions created: {created_questions}")
        self.stdout.write("")

    def parse_data(self, raw_text):
        blocks = [block.strip() for block in raw_text.split("---") if block.strip()]

        if not blocks:
            raise CommandError("Invalid data format.")

        header = self.parse_key_values(blocks[0])

        title = header.get("title", "").strip()
        if not title:
            raise CommandError("Missing TITLE.")

        result = {
            "title": title,
            "audio": header.get("audio", "").strip(),
            "instructions": header.get("instructions", "").strip(),
            "transcript": header.get("transcript", "").strip(),
            "description": header.get("description", "").strip(),
            "questions": [],
        }

        for block in blocks[1:]:
            item = self.parse_key_values(block)

            question_text = item.get("q", "").strip() or item.get("question", "").strip()
            if not question_text:
                continue

            answer = item.get("answer", "A").strip().upper()[:1] or "A"

            if answer not in ["A", "B", "C", "D", "E", "F"]:
                answer = "A"

            result["questions"].append({
                "question": question_text,
                "a": item.get("a", "").strip(),
                "b": item.get("b", "").strip(),
                "c": item.get("c", "").strip(),
                "d": item.get("d", "").strip(),
                "e": item.get("e", "").strip(),
                "f": item.get("f", "").strip(),
                "answer": answer,
                "explanation": item.get("explanation", "").strip(),
            })

        if not result["questions"]:
            raise CommandError("No valid questions found.")

        return result

    def parse_key_values(self, text):
        data = {}
        current_key = None

        for raw_line in text.splitlines():
            line = raw_line.rstrip()

            if not line.strip():
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key:
                    current_key = key
                    data[current_key] = value
                    continue

            if current_key:
                data[current_key] += "\n" + line.strip()

        return data
