from pathlib import Path

# =========================
# 1) Edit view: không xóa audio_url khi cột Audio URL không còn trên form
# =========================
vp = Path("core/views.py")
v = vp.read_text(encoding="utf-8", errors="ignore")

v = v.replace(
'''                if hasattr(q, "audio_url"):
                    q.audio_url = request.POST.get(f"audio_url_{row_id}", "").strip()
''',
'''                audio_url_key = f"audio_url_{row_id}"
                if hasattr(q, "audio_url") and audio_url_key in request.POST:
                    q.audio_url = request.POST.get(audio_url_key, "").strip()
'''
)

v = v.replace(
'''                q.correct_answer = request.POST.get(f"correct_answer_{row_id}", "A").strip().upper()[:1] or "A"''',
'''                posted_correct = request.POST.get(f"correct_answer_{row_id}")
                if posted_correct is not None:
                    q.correct_answer = posted_correct.strip().upper()[:1] or q.correct_answer or "A"'''
)

vp.write_text(v, encoding="utf-8")


# =========================
# 2) Ghi lại template Part 1: bỏ Audio URL, chọn answer ngay trong A/B/C
# =========================
Path("templates/core/admin_part1_questions.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Manage Part 1 | Score TSA Với Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <style>
        :root{
            --red:#e60023;
            --red2:#ff5f76;
            --dark:#3f0011;
            --soft:#fff1f4;
            --line:#ffd1dc;
            --muted:#667085;
            --bg:#fff7f9;
            --white:#fff;
        }

        *{box-sizing:border-box}

        body{
            margin:0;
            font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
            background:linear-gradient(135deg,#fffafa,#ffecef);
            color:var(--dark);
        }

        a{text-decoration:none;color:inherit}

        .page{
            min-height:100vh;
            padding:24px;
        }

        .topbar{
            position:sticky;
            top:0;
            z-index:30;
            background:rgba(255,247,249,.90);
            backdrop-filter:blur(14px);
            border:1px solid var(--line);
            border-radius:26px;
            padding:18px 20px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:16px;
            box-shadow:0 16px 35px rgba(180,0,30,.08);
            margin-bottom:20px;
        }

        .topbar h1{
            margin:0;
            font-size:clamp(30px,4vw,48px);
            letter-spacing:-.04em;
        }

        .topbar p{
            margin:6px 0 0;
            color:var(--muted);
            font-size:15px;
        }

        .actions{
            display:flex;
            gap:10px;
            flex-wrap:wrap;
        }

        .btn{
            border:0;
            border-radius:999px;
            padding:12px 18px;
            font-weight:900;
            cursor:pointer;
            display:inline-flex;
            align-items:center;
            justify-content:center;
            gap:8px;
            white-space:nowrap;
        }

        .btn-primary{
            background:linear-gradient(135deg,var(--red),var(--red2));
            color:white;
            box-shadow:0 12px 24px rgba(230,0,35,.18);
        }

        .btn-ghost{
            background:white;
            color:#8a0015;
            border:1px solid var(--line);
        }

        .btn-danger{
            background:#8b000c;
            color:white;
            box-shadow:0 12px 24px rgba(139,0,12,.16);
        }

        .toolbar{
            background:white;
            border:1px solid var(--line);
            border-radius:24px;
            padding:18px;
            display:grid;
            grid-template-columns:1fr auto;
            gap:16px;
            align-items:center;
            margin-bottom:20px;
            box-shadow:0 16px 35px rgba(180,0,30,.06);
        }

        .searchbox{
            display:flex;
            align-items:center;
            gap:10px;
            background:#fff7f8;
            border:1px solid var(--line);
            border-radius:18px;
            padding:12px 14px;
        }

        .searchbox input{
            border:0;
            outline:0;
            background:transparent;
            width:100%;
            font-size:16px;
            color:var(--dark);
        }

        .create-form{
            display:flex;
            gap:10px;
            align-items:center;
        }

        .create-form input{
            width:88px;
            border:1px solid var(--line);
            border-radius:14px;
            padding:12px;
            font-weight:900;
            color:var(--dark);
        }

        .stat-row{
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:14px;
            margin-bottom:20px;
        }

        .stat-card{
            background:white;
            border:1px solid var(--line);
            border-radius:22px;
            padding:16px;
            box-shadow:0 12px 28px rgba(180,0,30,.05);
        }

        .stat-card span{
            display:block;
            color:var(--muted);
            font-weight:750;
            font-size:13px;
            margin-bottom:8px;
        }

        .stat-card strong{
            font-size:32px;
            color:var(--red);
        }

        .bulk-card{
            background:white;
            border:1px solid var(--line);
            border-radius:26px;
            box-shadow:0 18px 40px rgba(180,0,30,.08);
            overflow:hidden;
        }

        .bulk-head{
            padding:18px 20px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:16px;
            border-bottom:1px solid var(--line);
            background:linear-gradient(180deg,#fff,#fff7f8);
        }

        .bulk-head h2{
            margin:0;
            font-size:24px;
        }

        .bulk-head p{
            margin:5px 0 0;
            color:var(--muted);
        }

        .bulk-tools{
            display:flex;
            gap:10px;
            flex-wrap:wrap;
            justify-content:flex-end;
        }

        .table-wrap{
            overflow:auto;
            max-height:calc(100vh - 330px);
        }

        table{
            border-collapse:collapse;
            width:100%;
            min-width:1550px;
        }

        th,td{
            border-bottom:1px solid #ffe0e5;
            border-right:1px solid #fff2f4;
            padding:10px;
            vertical-align:top;
        }

        th{
            position:sticky;
            top:0;
            z-index:5;
            background:#fff0f3;
            color:#720010;
            font-size:12px;
            text-transform:uppercase;
            letter-spacing:.04em;
            text-align:left;
        }

        tbody tr:hover td{
            background:#fffafb;
        }

        .col-check{width:62px;text-align:center}
        .col-lock{width:95px}
        .col-num{width:86px}
        .col-question{width:300px}
        .col-audio{width:290px}
        .col-answer{width:220px}
        .col-transcript{width:360px}

        input,textarea,select{
            width:100%;
            border:1px solid #ffd0d9;
            background:#fffafa;
            color:#1f2937;
            border-radius:13px;
            padding:10px;
            font:inherit;
            outline:none;
        }

        textarea{
            resize:vertical;
            min-height:62px;
            line-height:1.45;
        }

        input:focus,textarea:focus,select:focus{
            border-color:var(--red);
            box-shadow:0 0 0 4px rgba(230,0,35,.08);
            background:white;
        }

        .num-input{
            text-align:center;
            font-weight:900;
        }

        .row-check{
            width:20px;
            height:20px;
            accent-color:var(--red);
            cursor:pointer;
        }

        .lock-btn{
            border-radius:12px;
            padding:10px 12px;
            font-weight:900;
            cursor:pointer;
            width:100%;
            border:1px solid #ffc8d3;
            background:#fff7f8;
            color:#7a0010;
        }

        .answer-cell{
            display:grid;
            gap:9px;
        }

        .answer-choice{
            display:flex;
            align-items:center;
            gap:9px;
            padding:9px 10px;
            border:1px solid #ffd0d9;
            border-radius:13px;
            background:#fff7f8;
            color:#800012;
            font-weight:900;
            cursor:pointer;
            user-select:none;
        }

        .answer-choice input{
            width:18px;
            height:18px;
            accent-color:var(--red);
            cursor:pointer;
        }

        .answer-choice:has(input:checked){
            background:linear-gradient(135deg,#e60023,#ff5f76);
            color:white;
            border-color:#e60023;
            box-shadow:0 10px 20px rgba(230,0,35,.15);
        }

        tr.locked-row td{
            background:#fff8f9 !important;
        }

        tr.locked-row textarea,
        tr.locked-row input:not(.row-check):not(.answer-radio),
        tr.locked-row select{
            background:#f3f4f6;
            color:#6b7280;
            border-color:#e5e7eb;
            pointer-events:none;
        }

        tr.locked-row .answer-choice{
            pointer-events:none;
            opacity:.65;
        }

        tr.locked-row .lock-btn{
            background:#e60023;
            color:white;
            border-color:#e60023;
        }

        .sticky-save{
            position:sticky;
            bottom:0;
            z-index:10;
            padding:16px 20px;
            background:linear-gradient(180deg,rgba(255,255,255,.70),#fff);
            border-top:1px solid var(--line);
            display:flex;
            justify-content:flex-end;
            gap:10px;
            flex-wrap:wrap;
        }

        .message{
            margin-bottom:16px;
            padding:14px 18px;
            border-radius:18px;
            background:#fff1f4;
            border:1px solid var(--line);
            color:#7a0010;
            font-weight:850;
        }

        @media(max-width:1000px){
            .toolbar{grid-template-columns:1fr}
            .stat-row{grid-template-columns:repeat(2,1fr)}
            .topbar{flex-direction:column;align-items:stretch}
            .actions{justify-content:flex-start}
        }

        @media(max-width:650px){
            .stat-row{grid-template-columns:1fr}
            .page{padding:14px}
        }
    </style>
</head>

<body>
<div class="page">
    <header class="topbar">
        <div>
            <h1>Manage Part 1 Questions</h1>
            <p>Bulk update data: audio, questions, answers, and transcripts.</p>
        </div>

        <div class="actions">
            <a class="btn btn-ghost" href="{% url 'admin_listening_parts' %}">← Choose Part</a>
            <a class="btn btn-ghost" href="{% url 'dashboard' %}">Overview</a>
            <a class="btn btn-primary" href="{% url 'logout' %}">Exit</a>
        </div>
    </header>

    {% if messages %}
        {% for message in messages %}
            <div class="message">{{ message }}</div>
        {% endfor %}
    {% endif %}

    <section class="stat-row">
        <div class="stat-card">
            <span>Total Part 1 Questions</span>
            <strong>{{ total_questions }}</strong>
        </div>
        <div class="stat-card">
            <span>Audio Available</span>
            <strong>{{ audio_count|default:0 }}</strong>
        </div>
        <div class="stat-card">
            <span>Missing Questions</span>
            <strong>{{ empty_question_count|default:0 }}</strong>
        </div>
        <div class="stat-card">
            <span>Editing</span>
            <strong>Part 1</strong>
        </div>
    </section>

    <section class="toolbar">
        <div class="searchbox">
            <strong>🔎</strong>
            <input id="quickSearch" type="text" placeholder="Quick search by question number, content, transcript, or answer...">
        </div>

        <form method="post" class="create-form">
            {% csrf_token %}
            <input type="hidden" name="action" value="create_blank">
            <input type="number" name="create_count" min="1" max="100" value="10">
            <button class="btn btn-ghost" type="submit">+ Add Row</button>
        </form>
    </section>

    <form method="post" class="bulk-card" id="bulkForm">
        {% csrf_token %}
        <input type="hidden" name="action" value="save_all">

        <div class="bulk-head">
            <div>
                <h2>Bulk Update Table</h2>
                <p>Select the radio button in column A/B/C to set the correct answer. The Audio URL column has been removed.</p>
            </div>

            <div class="bulk-tools">
                <button class="btn btn-ghost" type="button" onclick="toggleAllLocks()">🔒 Lock/Unlock All</button>
                <button class="btn btn-danger" type="submit" onclick="return deleteSelectedRows()">🗑️ Delete Selected Rows</button>
                <button class="btn btn-primary" type="submit" onclick="setSaveAction()">💾 Save All</button>
            </div>
        </div>

        <div class="table-wrap">
            <table id="part1Table">
                <thead>
                    <tr>
                        <th class="col-check"><input type="checkbox" class="row-check" id="checkAll"></th>
                        <th class="col-lock">Lock</th>
                        <th class="col-num">No.</th>
                        <th class="col-question">Question</th>
                        <th class="col-audio">Audio Drive</th>
                        <th class="col-answer">Answer A</th>
                        <th class="col-answer">Answer B</th>
                        <th class="col-answer">Answer C</th>
                        <th class="col-transcript">Transcript</th>
                    </tr>
                </thead>

                <tbody>
                {% for q in questions %}
                    <tr>
                        <td>
                            <input class="row-check item-check" type="checkbox" name="selected_id" value="{{ q.id }}">
                        </td>

                        <td>
                            <button class="lock-btn" type="button" onclick="toggleRowLock(this)">🔓 Open</button>
                        </td>

                        <td>
                            <input type="hidden" name="row_id" value="{{ q.id }}">
                            <input class="num-input" type="number" name="question_number_{{ q.id }}" value="{{ q.question_number }}">
                        </td>

                        <td>
                            <textarea name="question_text_{{ q.id }}" rows="3" placeholder="Nhập nội dung questions...">{{ q.question_text }}</textarea>
                        </td>

                        <td>
                            <textarea name="audio_drive_link_{{ q.id }}" rows="3" placeholder="Dán link Google Drive MP3...">{% if q.audio_drive_link %}{{ q.audio_drive_link }}{% endif %}</textarea>
                        </td>

                        <td>
                            <div class="answer-cell">
                                <label class="answer-choice">
                                    <input class="answer-radio" type="radio" name="correct_answer_{{ q.id }}" value="A" {% if q.correct_answer == "A" %}checked{% endif %}>
                                    Chọn A là answer đúng
                                </label>
                                <textarea name="option_a_{{ q.id }}" rows="2" placeholder="Answer A">{{ q.option_a }}</textarea>
                            </div>
                        </td>

                        <td>
                            <div class="answer-cell">
                                <label class="answer-choice">
                                    <input class="answer-radio" type="radio" name="correct_answer_{{ q.id }}" value="B" {% if q.correct_answer == "B" %}checked{% endif %}>
                                    Chọn B là answer đúng
                                </label>
                                <textarea name="option_b_{{ q.id }}" rows="2" placeholder="Answer B">{{ q.option_b }}</textarea>
                            </div>
                        </td>

                        <td>
                            <div class="answer-cell">
                                <label class="answer-choice">
                                    <input class="answer-radio" type="radio" name="correct_answer_{{ q.id }}" value="C" {% if q.correct_answer == "C" %}checked{% endif %}>
                                    Chọn C là answer đúng
                                </label>
                                <textarea name="option_c_{{ q.id }}" rows="2" placeholder="Answer C">{{ q.option_c }}</textarea>
                            </div>
                        </td>

                        <td>
                            <textarea name="listening_transcript_{{ q.id }}" rows="3" placeholder="Transcript/dialogue...">{{ q.listening_transcript }}</textarea>
                        </td>
                    </tr>
                {% empty %}
                    <tr>
                        <td colspan="9">
                            Chưa có dòng nào. Hãy bấm “Tạo dòng”.
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="sticky-save">
            <button class="btn btn-ghost" type="button" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑ Lên đầu</button>
            <button class="btn btn-ghost" type="button" onclick="toggleAllLocks()">🔒 Lock/Unlock All</button>
            <button class="btn btn-danger" type="submit" onclick="return deleteSelectedRows()">🗑️ Delete Selected Rows</button>
            <button class="btn btn-primary" type="submit" onclick="setSaveAction()">💾 Save All Part 1</button>
        </div>
    </form>
</div>

<script>
function setSaveAction(){
    const action = document.querySelector("input[name='action']");
    if(action){ action.value = "save_all"; }
}

function deleteSelectedRows(){
    const action = document.querySelector("input[name='action']");
    const checked = document.querySelectorAll(".item-check:checked").length;

    if(checked === 0){
        alert("Bạn chưa chọn dòng nào để xóa.");
        return false;
    }

    if(action){ action.value = "delete_selected"; }
    return confirm("Delete " + checked + " dòng đã chọn?");
}

function toggleRowLock(btn){
    const row = btn.closest("tr");
    row.classList.toggle("locked-row");
    const locked = row.classList.contains("locked-row");
    btn.textContent = locked "🔒 Lock" : "🔓 Open";
}

function toggleAllLocks(){
    const rows = document.querySelectorAll("#part1Table tbody tr");
    const hasUnlocked = Array.from(rows).some(row => !row.classList.contains("locked-row"));

    rows.forEach(row => {
        if(hasUnlocked){
            row.classList.add("locked-row");
            const btn = row.querySelector(".lock-btn");
            if(btn) btn.textContent = "🔒 Lock";
        }else{
            row.classList.remove("locked-row");
            const btn = row.querySelector(".lock-btn");
            if(btn) btn.textContent = "🔓 Open";
        }
    });
}

const checkAll = document.getElementById("checkAll");
if(checkAll){
    checkAll.addEventListener("change", function(){
        document.querySelectorAll(".item-check").forEach(cb => cb.checked = checkAll.checked);
    });
}

const search = document.getElementById("quickSearch");
const table = document.getElementById("part1Table");

if(search && table){
    search.addEventListener("input", function(){
        const key = this.value.toLowerCase().trim();
        table.querySelectorAll("tbody tr").forEach(function(row){
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(key) "" : "none";
        });
    });
}
</script>
</body>
</html>
''', encoding="utf-8")

print("DA_XOA_AUDIO_URL_VA_CHON_DAP_AN_TRONG_COT_ABC")
