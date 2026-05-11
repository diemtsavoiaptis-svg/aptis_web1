from pathlib import Path
import ast
import re

# 1. Create response middleware that cleans visible HTML text before browser receives it
middleware_path = Path("core/english_ui_middleware.py")

middleware_code = r'''
class EnglishUIMiddleware:
    """
    Final UI text cleanup layer.
    It runs on rendered HTML responses and replaces remaining Vietnamese/mojibake UI text with English.
    """

    REPLACEMENTS = {
        # Global brand/title
        "Score TSA Vß╗¢i Aptis": "Aptis Learning Platform",
        "Score TSA V├¼ Aptis": "Aptis Learning Platform",
        "?i?m TSA V? Aptis": "Aptis Learning Platform",
        "?i?m TSA VAptis": "Aptis Learning Platform",
        "?i?m TSA V?i Aptis": "Aptis Learning Platform",
        "Điểm TSA Với Aptis": "Aptis Learning Platform",
        "Score TSA Với Aptis": "Aptis Learning Platform",

        # Broken symbols
        "ΓåÉ": "←",
        "ΓåÆ": "→",
        "Γå╗": "↻",
        "Γû╢": "▶",
        "≡ƒÆ╛": "💾",
        "≡ƒùæ∩╕Å": "🗑️",
        "≡ƒùæ": "🗑️",
        "ΓÇÖ": "'",
        "ΓÇ£": "\"",
        "ΓÇ¥": "\"",
        "ΓÇó": "•",
        "ΓÇô": "-",
        "ΓÇö": "—",
        "┬╖": "·",

        # Dashboard / choose part
        "Hiß╗ân thß╗ï 4 part theo dß║íng thß║╗ bo tr├▓n. Part 1 v├á Part 2 data locked;": "Display 4 parts as rounded cards. Part 1 and Part 2 data are locked;",
        "Part 3 v├á Part 4 ─æang ─æß╗â trß╗æng for upcoming design work.": "Part 3 and Part 4 are empty for upcoming design work.",
        "Mß╗ƒ Part 1": "Open Part 1",
        "Mß╗ƒ Part 2": "Open Part 2",
        "Mß╗ƒ Part 3": "Open Part 3",
        "Mß╗ƒ Part 4": "Open Part 4",

        # Part 1
        "Chß╗ìn A l├á answer ─æ├║ng": "Select A as the correct answer",
        "Chß╗ìn B l├á answer ─æ├║ng": "Select B as the correct answer",
        "Chß╗ìn C l├á answer ─æ├║ng": "Select C as the correct answer",
        "Trang ch├¡nh": "Home",
        "Listening Practice tß╗½ng c├óu, r├╡ r├áng v├á dß╗à thao t├íc.": "Question-by-question listening practice with a clear and easy-to-use layout.",
        "C├óu 1/191": "Question 1/191",
        "C├óu 1": "Question 1",
        "─É╞░ß╗úc bß║úo vß╗ç": "Protected",
        "Kiß╗âm tra answer": "Check Answer",
        "C├óu tiß║┐p theo": "Next Question",

        # Part 2 choose/list/detail
        "Admin Part 2 - Chß╗ìn version": "Admin Part 2 - Choose Version",
        "Listening Part 2 - Chß╗ìn version": "Listening Part 2 - Choose Version",
        "Chß╗ìn version b├ái l├ám tr╞░ß╗¢c khi v├áo danh s├ích topics.": "Choose a version before opening the topic list.",
        "Mß╗ùi topics c├│ 1 file nghe tß╗òng v├á 1 c├óu data tß╗òng.": "Each topic has one shared listening file and one shared answer data set.",
        "Mß╗ùi topics c├│ 4 voice t╞░╞íng ß╗⌐ng 4 ng╞░ß╗¥i / 4 ├╜ data.": "Each topic has 4 voices for 4 speakers and 4 answer data sets.",
        "Chß╗ìn topics ─æß╗â bß║»t ─æß║ºu l├ám b├ái.": "Choose a topic to start the practice.",
        "Chß╗º ─æß╗ü M├áy giß╗Åi": "Version A Topic",
        "Chß╗º ─æß╗ü M├áy k├⌐m": "Version B Topic",
        "Topic Studying phi├¬n bß║ún 2.": "Topic Studying version 2.",
        "Ch╞░a c├│ topics": "No topics yet",
        "Admin ch╞░a nhß║¡p data cho version n├áy.": "The admin has not entered data for this version yet.",
        "1 file nghe chung": "1 shared listening file",
        ". Nhß║¡p data answer tß╗òng tr╞░ß╗¢c, sau ─æ├│ chß╗ìn answer ─æ├║ng b├¬n d╞░ß╗¢i.": ". Enter the shared answer data first, then choose the correct answer below.",
        "Danh s├ích 12 topics": "12 Topic List",
        "Danh s├ích topics": "Topic List",
        "T├¬n topic": "Topic Name",
        "T├¬n topics": "Topic Name",
        "M├┤ tß║ú": "Description",
        "M├┤ tß║ú / ghi ch├║": "Description / Notes",
        "Audio Drive chung cß╗ºa topics": "Shared Topic Audio Drive",
        "─É├ú c├│ link audio:": "Audio link available:",
        "Mß╗ƒ file nghe": "Open Listening File",
        "Data answer tß╗òng": "Shared Answer Data",
        "Save answer tß╗òng": "Save Shared Answers",
        "Nß╗Öi dung voice / Transcript": "Voice Content / Transcript",
        "Ch╞░a c├│ transcript cho topic n├áy. Nß║┐u ─æ├ú chß║íy lß╗çnh nhß║¡p 12 topic m├á vß║½n trß╗æng, kiß╗âm tra lß║íi data topic trong database.": "There is no transcript for this topic yet. Check the topic data in the database.",
        "Chß╗ìn answer ─æ├║ng cho 4 Person": "Choose the correct answer for 4 people",
        "-- Chß╗ìn answer ─æ├║ng --": "-- Choose the correct answer --",
        "Save answer ─æ├║ng": "Save Correct Answers",
        "Bß║úng data Part 2: mß╗ùi topics c├│ 4 voice t╞░╞íng ß╗⌐ng 4 ng╞░ß╗¥i. Mß╗ùi voice c├│ audio, A/B/C/D, transcript v├á data answer.": "Part 2 data table: each topic has 4 voices for 4 speakers. Each voice has audio, A/B/C/D answers, transcript, and answer data.",
        "Cß╗Öt ΓÇ£Data answerΓÇ¥ c├│ thß╗â nhß║¡p nhiß╗üu d├▓ng, nh╞░ng khi l├ám b├ái chß╗ë khai th├íc 4 data t╞░╞íng ß╗⌐ng 4 ng╞░ß╗¥i.": "The Answer Data column can contain multiple lines, but the student practice only uses the 4 answer data items for 4 speakers.",
        "File audio cß╗ºa topics": "Topic Audio File",
        "File nghe cß╗ºa topics": "Topic Listening File",
        "Nß╗Öi dung file ghi ├óm": "Recording Transcript",
        "Data cß╗ºa c├íc answer": "Answer Data",
        "Save data topics": "Save Topic Data",
        "Delete topics n├áy": "Delete This Topic",
        "Exit b├ái": "Exit Practice",

        # Part 3 / Part 4 placeholders
        "Manage Part 3 | ?i?m TSA V? Aptis": "Manage Part 3 | Aptis Learning Platform",
        "Interface Part 3 ?? ???c l?m s?ch. Ph?n topic c?a Part 2 kh?ng c?n hi?n th? ? ??y.": "The Part 3 interface has been cleaned. Part 2 topics should not appear here.",
        "Khi c? d? li?u/topic ri?ng cho Part 3, m?nh s? thi?t k? ti?p ??ng c?u tr?c m?i.": "When separate Part 3 data/topics are available, the new structure will be designed here.",
        "Part 3 ch?a c? topic": "Part 3 has no topics yet",
        "Hi?n ch?a t?o danh s?ch ch? ?? cho Part 3.": "No topic list has been created for Part 3 yet.",
        "Khu v?c n?y ???c ?? tr?ng ?? tr?nh d?ng nh?m 12 topic c?a Part 2.": "This area is intentionally left empty to avoid accidentally using the 12 Part 2 topics.",
        "Part 3 ch? d?ng 3 l?a ch?n tr? l?i c? ??nh:": "Part 3 only uses 3 fixed answer choices:",
        "Ng??i nam n?i / ch?n ??p ?n nam.": "The man speaks / choose the man answer.",
        "Ng??i n? n?i / ch?n ??p ?n n?.": "The woman speaks / choose the woman answer.",
        "C? hai ng??i ??u ??ng / ??u ???c nh?c ??n.": "Both people are correct / both are mentioned.",
        "? Quay l?i Dashboard": "← Back to Dashboard",
        "Khu v?c manage ri?ng cho Part 3. Hi?n t?i ch? gi? hai nh?m": "Separate management area for Part 3. It currently keeps only two groups.",
        "M?y gi?i": "Version A",
        "M?y k?m": "Version B",
        "Nh?m ch? ?? d?nh cho m?c gi?i c?a Part 3.": "Topic group for the advanced Part 3 level.",
        "Ph?n M?y gi?i c?a Part 3 hi?n ?ang tr?ng.": "The Version A area of Part 3 is currently empty.",
        "Ph?n M?y k?m c?a Part 3 hi?n ?ang tr?ng.": "The Version B area of Part 3 is currently empty.",
        "Part 3 d?ng ??p ?n c? ??nh:": "Part 3 uses fixed answer choices:",

        # Students
        "Duyß╗çt student": "Student Approval",
        "Tra student": "Search Student",
        "Nhß║¡p t├¬n, Gmail, S─ÉT hoß║╖c ID student.": "Enter student name, Gmail, phone number, or student ID.",
        "Information cß║ºn tra": "Information to Search",
        "Hß╗ô s╞í student": "Student Profile",
        "Update Gmail, S─ÉT, t├¬n v├á ID student.": "Update Gmail, phone number, name, and student ID.",
        "Ch╞░a chß╗ìn student. H├úy tra student b├¬n tr├íi tr╞░ß╗¢c.": "No student selected. Search for a student on the left first.",
        "Hß╗ô s╞í ─æ├ú l╞░u": "Saved Profiles",
        "Danh s├ích student ─æ├ú c├│ hß╗ô s╞í trong hß╗ç thß╗æng.": "List of students with saved profiles in the system.",
        "T├¬n": "Name",
        "Sß╗æ ─æiß╗çn thoß║íi": "Phone Number",
        "Thao t├íc": "Actions",
        "d┼⌐ng": "Stop",
        "Mß╗ƒ hß╗ô s╞í": "Open Profile",
        "Delete hß╗ô s╞í": "Delete Profile",

        # Lessons / thumbnail / background
        "Manage lesson": "Manage Lessons",
        "Mß╗Ñc lesson ─æ├ú mß╗ƒ. C├│ thß╗â tiß║┐p tß╗Ñc th├¬m interface manage video/nß╗Öi dung lesson sau.": "The lesson section is open. A video/content management interface can be added later.",
        "Thumbnail m?n h?nh login": "Login Screen Thumbnail",
        "Interface basic: ch? th?m ?nh, k?o ?nh trong preview r?i l?u.": "Basic interface: add images, drag them inside the preview, then save.",
        "K?o ?nh ?? ??t v? tr?. Admin kh?ng ph?ng to ?nh khi hover n?a.": "Drag images to set their position. Admin no longer zooms images on hover.",
        "?? L?y thumbnail t? video": "Get Thumbnail from Video",
        "M?o: ph?t video ??n ??ng b? c?c b?n mu?n, r?i b?m n?t n?y ?? ch?p frame l?m thumbnail.": "Tip: play the video to the frame you want, then click this button to capture it as a thumbnail.",
        "Th?m ?nh": "Add Image",
        "+ Th?m ?nh": "+ Add Image",
        "Ch?a c? ?nh n?i": "No Floating Images Yet",
        "B?m + Th?m ?nh ?? upload ?nh ??u ti?n.": "Click + Add Image to upload the first image.",
        "?? L?u to?n b? interface": "Save Full Interface",
        "C├ái ─æß║╖t ß║únh nß╗ün interface": "Background Image Settings",
        "Tß║úi ß║únh nß╗ün mß╗¢i cho trang chß╗º hoß║╖c thay ─æß╗òi ß║únh hiß╗çn tß║íi.": "Upload a new background image for the home page or replace the current image.",
        "ß║ónh nß╗ün hiß╗çn tß║íi": "Current Background",
        "Ch╞░a c├│ ß║únh nß╗ün t├╣y chß╗ënh.": "No custom background image yet.",
        "Home ─æang d├╣ng nß╗ün mß║╖c ─æß╗ïnh.": "Home is using the default background.",
        "ß║ónh nß╗ün mß║╖c ─æß╗ïnh": "Default Background",
        "Ch╞░a c├│ ß║únh t├╣y chß╗ënh": "No custom image yet",
        "Tß║úi ß║únh nß╗ün mß╗¢i": "Upload New Background",
        "Chß╗ìn ß║únh tß╗½ m├íy": "Choose Image from Computer",
        "K├⌐o & thß║ú ß║únh v├áo ─æ├óy": "Drag and drop an image here",
        "hoß║╖c nhß║Ñp ─æß╗â chß╗ìn tß╗çp": "or click to choose a file",
        "─Éß╗ïnh dß║íng: JPG, PNG, WebP ΓÇó Khuyß║┐n nghß╗ï: 1920├ù1080 hoß║╖c lß╗¢n h╞ín.": "Formats: JPG, PNG, WebP • Recommended: 1920×1080 or larger.",
        "HOß║╢C": "OR",
        "Hoß║╖c d├ín ─æ╞░ß╗¥ng dß║½n ß║únh": "Or paste an image URL",
        "T├¬n ß║únh": "Image Name",
        "Save ß║únh nß╗ün": "Save Background",
        "Delete ß║únh hiß╗çn tß║íi": "Delete Current Image",
        "Kh├┤i phß╗Ñc mß║╖c ─æß╗ïnh": "Restore Default",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response

        try:
            html = response.content.decode("utf-8", errors="replace")
        except Exception:
            return response

        for old, new in sorted(self.REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
            html = html.replace(old, new)

        # Final safety for corrupted titles
        html = re_sub(r"Score TSA V.{0,20} Aptis", "Aptis Learning Platform", html)
        html = re_sub(r"\?i\?m TSA V.{0,20} Aptis", "Aptis Learning Platform", html)

        response.content = html.encode("utf-8")
        if "Content-Length" in response:
            del response["Content-Length"]
        return response


def re_sub(pattern, replacement, text):
    import re
    return re.sub(pattern, replacement, text, flags=re.I)
'''

middleware_path.write_text(middleware_code, encoding="utf-8")

# 2. Add middleware to settings.py
settings_path = Path("config/settings.py")
text = settings_path.read_text(encoding="utf-8", errors="replace")

middleware_name = "core.english_ui_middleware.EnglishUIMiddleware"

if middleware_name not in text:
    marker = "MIDDLEWARE = ["
    if marker in text:
        text = text.replace(marker, f'MIDDLEWARE = [\n    "{middleware_name}",', 1)
    else:
        raise SystemExit("MIDDLEWARE list not found in config/settings.py")

settings_path.write_text(text, encoding="utf-8")

print("English UI middleware installed.")
