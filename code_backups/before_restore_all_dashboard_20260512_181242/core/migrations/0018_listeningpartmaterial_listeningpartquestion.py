from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_listeningquestion_voice_info_locked"),
    ]

    operations = [
        migrations.CreateModel(
            name="ListeningPartMaterial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("part", models.IntegerField(choices=[(3, "Part 3"), (4, "Part 4")], verbose_name="Part")),
                ("title", models.CharField(max_length=255, verbose_name="Tên tài liệu")),
                ("description", models.TextField(blank=True, verbose_name="Mô tả ngắn")),
                ("instructions", models.TextField(blank=True, verbose_name="Hướng dẫn làm bài")),
                ("audio_url", models.URLField(blank=True, verbose_name="Link audio / Google Drive")),
                ("document_file", models.FileField(blank=True, null=True, upload_to="listening_part34_documents/", verbose_name="Tài liệu đính kèm")),
                ("transcript", models.TextField(blank=True, verbose_name="Transcript / nội dung nghe")),
                ("is_active", models.BooleanField(default=True, verbose_name="Hiển thị cho học viên")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")),
            ],
            options={
                "verbose_name": "Tài liệu Listening Part 3/4",
                "verbose_name_plural": "Tài liệu Listening Part 3/4",
                "ordering": ["part", "id"],
            },
        ),
        migrations.CreateModel(
            name="ListeningPartQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(default=1, verbose_name="STT")),
                ("question_text", models.TextField(verbose_name="Câu hỏi")),
                ("option_a", models.CharField(blank=True, max_length=500, verbose_name="Đáp án A")),
                ("option_b", models.CharField(blank=True, max_length=500, verbose_name="Đáp án B")),
                ("option_c", models.CharField(blank=True, max_length=500, verbose_name="Đáp án C")),
                ("option_d", models.CharField(blank=True, max_length=500, verbose_name="Đáp án D")),
                ("option_e", models.CharField(blank=True, max_length=500, verbose_name="Đáp án E")),
                ("option_f", models.CharField(blank=True, max_length=500, verbose_name="Đáp án F")),
                ("correct_answer", models.CharField(choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E"), ("F", "F")], default="A", max_length=1, verbose_name="Đáp án đúng")),
                ("explanation", models.TextField(blank=True, verbose_name="Giải thích / ghi chú")),
                ("material", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="core.listeningpartmaterial", verbose_name="Tài liệu")),
            ],
            options={
                "verbose_name": "Câu hỏi Listening Part 3/4",
                "verbose_name_plural": "Câu hỏi Listening Part 3/4",
                "ordering": ["material_id", "order", "id"],
            },
        ),
    ]
