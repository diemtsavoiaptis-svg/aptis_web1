import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "db.sqlite3"
OUT_DIR = ROOT / "vercel_static" / "data"


def extract_drive_file_id(value):
    text = str(value or "")
    markers = ["/file/d/", "/d/"]

    for marker in markers:
        if marker in text:
            return text.split(marker, 1)[1].split("/", 1)[0].split("?", 1)[0]

    if "id=" in text:
        return text.split("id=", 1)[1].split("&", 1)[0]

    return ""


def export_part(part):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    rows = con.execute(
        """
        select
          question_number,
          question_text,
          option_a,
          option_b,
          option_c,
          correct_answer,
          listening_transcript,
          audio_drive_link,
          audio_drive_file_id
        from core_listeningquestion
        where part = ?
        order by question_number, id
        """,
        (part,),
    ).fetchall()

    questions = []

    for row in rows:
        drive_link = row["audio_drive_link"] or ""
        drive_file_id = row["audio_drive_file_id"] or extract_drive_file_id(drive_link)
        questions.append(
            {
                "number": row["question_number"],
                "question": row["question_text"] or "",
                "options": {
                    "A": row["option_a"] or "",
                    "B": row["option_b"] or "",
                    "C": row["option_c"] or "",
                },
                "correctAnswer": (row["correct_answer"] or "A").strip().upper(),
                "transcript": row["listening_transcript"] or "",
                "audioDriveLink": drive_link,
                "audioDriveFileId": drive_file_id,
            }
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"listening-part-{part}.json"
    out_path.write_text(
        json.dumps(
            {
                "part": part,
                "totalQuestions": len(questions),
                "questions": questions,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return out_path, len(questions)


if __name__ == "__main__":
    path, count = export_part(1)
    print(f"Exported {count} questions to {path}")
