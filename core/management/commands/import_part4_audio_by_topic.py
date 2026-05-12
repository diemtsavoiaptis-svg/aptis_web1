from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import ListeningPartMaterial
import re


class Command(BaseCommand):
    help = "Import Part 4 audio links by topic/file name."

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Listening Part 4 Audio Import"))
        self.stdout.write("Please paste your audio data below. When finished, type END on a new line.")
        self.stdout.write("")
        self.stdout.write("Format:")
        self.stdout.write("Tên File<TAB>Link File")
        self.stdout.write("A break from studying.mp3<TAB>https://drive.google.com/...")
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
            raise CommandError("No audio data pasted.")

        materials = list(ListeningPartMaterial.objects.filter(part=4).order_by("id"))
        topic_map = {self.normalize(m.title): m for m in materials}

        updated = 0
        skipped = 0
        missing = []

        with transaction.atomic():
            for line_number, line in enumerate(lines, start=1):
                parts = self.split_row(line)

                if len(parts) < 2:
                    skipped += 1
                    continue

                file_name = parts[0].strip()
                audio_url = parts[1].strip()

                if self.looks_like_header(file_name, audio_url):
                    skipped += 1
                    continue

                if not audio_url.startswith("http"):
                    skipped += 1
                    continue

                topic_key = self.normalize(file_name)
                material = topic_map.get(topic_key)

                if not material:
                    missing.append(file_name)
                    skipped += 1
                    continue

                material.audio_url = audio_url
                material.save(update_fields=["audio_url"])
                updated += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Audio import completed."))
        self.stdout.write(f"Updated audio links: {updated}")
        self.stdout.write(f"Skipped rows: {skipped}")

        if missing:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Missing topic matches:"))
            for item in missing:
                self.stdout.write(f"- {item}")

        total = ListeningPartMaterial.objects.filter(part=4).count()
        audio_count = ListeningPartMaterial.objects.filter(part=4).exclude(audio_url="").count()
        missing_audio = ListeningPartMaterial.objects.filter(part=4, audio_url="").count()

        self.stdout.write("")
        self.stdout.write(f"Part 4 total: {total}")
        self.stdout.write(f"Audio links: {audio_count}")
        self.stdout.write(f"Missing audio: {missing_audio}")
        self.stdout.write("")

    def split_row(self, line):
        if "\t" in line:
            return [x.strip() for x in line.split("\t")]
        if "|" in line:
            return [x.strip() for x in line.split("|")]
        return [x.strip() for x in line.split(",")]

    def normalize(self, value):
        value = (value or "").strip()
        value = re.sub(r"\.mp3$", "", value, flags=re.I)
        value = re.sub(r"^topic\s+", "", value, flags=re.I)
        value = re.sub(r"\s+4$", "", value, flags=re.I)
        value = re.sub(r"\s+", " ", value)
        return value.casefold()

    def looks_like_header(self, file_name, audio_url):
        text = f"{file_name} {audio_url}".casefold()
        return "tên file" in text or "link file" in text or "audio" in text
