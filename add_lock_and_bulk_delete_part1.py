from pathlib import Path
import re

# =========================
# 1) Sửa view: thêm xóa nhiều dòng đã chọn
# =========================
views_path = Path("core/views.py")
views = views_path.read_text(encoding="utf-8", errors="ignore")

if 'if action == "delete_selected":' not in views:
    views = views.replace(
'''        if action == "delete_one":
            delete_id = request.POST.get("delete_id")
            ListeningQuestion.objects.filter(id=delete_id, part=1).delete()
            messages.success(request, "Đã xóa 1 câu hỏi Part 1.")
            return redirect("admin_part1_questions")
''',
'''        if action == "delete_selected":
            selected_ids = request.POST.getlist("selected_id")
            deleted_count, _ = ListeningQuestion.objects.filter(id__in=selected_ids, part=1).delete()
            messages.success(request, f"Đã xóa {deleted_count} câu hỏi Part 1 đã chọn.")
            return redirect("admin_part1_questions")

        if action == "delete_one":
            delete_id = request.POST.get("delete_id")
            ListeningQuestion.objects.filter(id=delete_id, part=1).delete()
            messages.success(request, "Đã xóa 1 câu hỏi Part 1.")
            return redirect("admin_part1_questions")
'''
    )

views_path.write_text(views, encoding="utf-8")
print("DA_THEM_XOA_NHIEU_DONG")


# =========================
# 2) Ghi lại giao diện Part 1 có khóa + xóa ngoài
# =========================
Path("templates/core/admin_part1_questions.html").write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Quản lý Part 1 | Điểm TSA Với Aptis</title>
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
            min-width:1900px;
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
        .col-question{width:280px}
        .col-audio{width:260px}
        .col-answer{width:190px}
        .col-correct{width:90px}
        .col-transcript{width:320px}
        .col-delete{width:90px}

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

        .lock-btn,
        .delete-btn{
            border-radius:12px;
            padding:10px 12px;
            font-weight:900;
            cursor:pointer;
            width:100%;
        }

        .lock-btn{
            border:1px solid #ffc8d3;
            background:#fff7f8;
            color:#7a0010;
        }

        .delete-btn{
            border:1px solid #ffc8d3;
            background:#fff1f4;
            color:#c90016;
        }

        tr.locked-row td{
            background:#fff8f9 !important;
        }

        tr.locked-row textarea,
        tr.locked-row input:not(.row-check),
        tr.locked-row select{
            background:#f3f4f6;
            color:#6b7280;
            border-color:#e5e7eb;
            pointer-events:none;
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
            <h1>Quản lý câu hỏi Part 1</h1>
            <p>Cập nhật hàng loạt dữ liệu: audio, câu hỏi, đáp án và transcript.</p>
        </div>

        <div class="actions">
            <a class="btn btn-ghost" href="{% url 'admin_listening_parts' %}">← Chọn Part</a>
            <a class="btn btn-ghost" href="{% url 'dashboard' %}">Tổng quan</a>
            <a class="btn btn-primary" href="{% url 'logout' %}">Thoát</a>
        </div>
    </header>

    {% if messages %}
        {% for message in messages %}
            <div class="message">{{ message }}</div>
        {% endfor %}
    {% endif %}

    <section class="stat-row">
        <div class="stat-card">
            <span>Tổng câu Part 1</span>
            <strong>{{ total_questions }}</strong>
        </div>
        <div class="stat-card">
            <span>Audio đã có</span>
            <strong>{{ audio_count|default:0 }}</strong>
        </div>
        <div class="stat-card">
            <span>Chưa có câu hỏi</span>
            <strong>{{ empty_question_count|default:0 }}</strong>
        </div>
        <div class="stat-card">
            <span>Đang chỉnh</span>
            <strong>Part 1</strong>
        </div>
    </section>

    <section class="toolbar">
        <div class="searchbox">
            <strong>🔎</strong>
            <input id="quickSearch" type="text" placeholder="Tìm nhanh theo số câu, nội dung, transcript, đáp án...">
        </div>

        <form method="post" class="create-form">
            {% csrf_token %}
            <input type="hidden" name="action" value="create_blank">
            <input type="number" name="create_count" min="1" max="100" value="10">
            <button class="btn btn-ghost" type="submit">+ Tạo dòng</button>
        </form>
    </section>

    <form method="post" class="bulk-card" id="bulkForm">
        {% csrf_token %}
        <input type="hidden" name="action" value="save_all">

        <div class="bulk-head">
            <div>
                <h2>Bảng cập nhật hàng loạt</h2>
                <p>Khóa dòng để tránh sửa nhầm. Tích chọn rồi bấm “Xóa dòng đã chọn” để xóa hàng loạt.</p>
            </div>

            <div class="bulk-tools">
                <button class="btn btn-ghost" type="button" onclick="toggleAllLocks()">🔒 Khóa/Mở tất cả</button>
                <button class="btn btn-danger" type="submit" onclick="return deleteSelectedRows()">🗑️ Xóa dòng đã chọn</button>
                <button class="btn btn-primary" type="submit" onclick="setSaveAction()">💾 Lưu toàn bộ</button>
            </div>
        </div>

        <div class="table-wrap">
            <table id="part1Table">
                <thead>
                    <tr>
                        <th class="col-check">
                            <input type="checkbox" class="row-check" id="checkAll">
                        </th>
                        <th class="col-lock">Khóa</th>
                        <th class="col-num">STT</th>
                        <th class="col-question">Câu hỏi</th>
                        <th class="col-audio">Audio Drive</th>
                        <th class="col-audio">Audio URL</th>
                        <th class="col-answer">Đáp án A</th>
                        <th class="col-answer">Đáp án B</th>
                        <th class="col-answer">Đáp án C</th>
                        <th class="col-correct">Đúng</th>
                        <th class="col-transcript">Transcript</th>
                        <th class="col-delete">Xóa</th>
                    </tr>
                </thead>

                <tbody>
                {% for q in questions %}
                    <tr>
                        <td>
                            <input class="row-check item-check" type="checkbox" name="selected_id" value="{{ q.id }}">
                        </td>

                        <td>
                            <button class="lock-btn" type="button" onclick="toggleRowLock(this)">🔓 Mở</button>
                        </td>

                        <td>
                            <input type="hidden" name="row_id" value="{{ q.id }}">
                            <input class="num-input" type="number" name="question_number_{{ q.id }}" value="{{ q.question_number }}">
                        </td>

                        <td>
                            <textarea name="question_text_{{ q.id }}" rows="3" placeholder="Nhập nội dung câu hỏi...">{{ q.question_text }}</textarea>
                        </td>

                        <td>
                            <textarea name="audio_drive_link_{{ q.id }}" rows="3" placeholder="Dán link Google Drive MP3...">{% if q.audio_drive_link %}{{ q.audio_drive_link }}{% endif %}</textarea>
                        </td>

                        <td>
                            <textarea name="audio_url_{{ q.id }}" rows="3" placeholder="Hoặc link audio trực tiếp...">{% if q.audio_url %}{{ q.audio_url }}{% endif %}</textarea>
                        </td>

                        <td>
                            <textarea name="option_a_{{ q.id }}" rows="2" placeholder="Đáp án A">{{ q.option_a }}</textarea>
                        </td>

                        <td>
                            <textarea name="option_b_{{ q.id }}" rows="2" placeholder="Đáp án B">{{ q.option_b }}</textarea>
                        </td>

                        <td>
                            <textarea name="option_c_{{ q.id }}" rows="2" placeholder="Đáp án C">{{ q.option_c }}</textarea>
                        </td>

                        <td>
                            <select name="correct_answer_{{ q.id }}">
                                <option value="A" {% if q.correct_answer == "A" %}selected{% endif %}>A</option>
                                <option value="B" {% if q.correct_answer == "B" %}selected{% endif %}>B</option>
                                <option value="C" {% if q.correct_answer == "C" %}selected{% endif %}>C</option>
                            </select>
                        </td>

                        <td>
                            <textarea name="listening_transcript_{{ q.id }}" rows="3" placeholder="Transcript/lời thoại...">{{ q.listening_transcript }}</textarea>
                        </td>

                        <td>
                            <button class="delete-btn" type="submit" name="delete_id" value="{{ q.id }}" onclick="return deleteOneRow(this)">Xóa</button>
                        </td>
                    </tr>
                {% empty %}
                    <tr>
                        <td colspan="12">
                            Chưa có dòng nào. Hãy bấm “Tạo dòng”.
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="sticky-save">
            <button class="btn btn-ghost" type="button" onclick="window.scrollTo({top:0,behavior:'smooth'})">↑ Lên đầu</button>
            <button class="btn btn-ghost" type="button" onclick="toggleAllLocks()">🔒 Khóa/Mở tất cả</button>
            <button class="btn btn-danger" type="submit" onclick="return deleteSelectedRows()">🗑️ Xóa dòng đã chọn</button>
            <button class="btn btn-primary" type="submit" onclick="setSaveAction()">💾 Lưu toàn bộ Part 1</button>
        </div>
    </form>
</div>

<script>
function setSaveAction(){
    const action = document.querySelector("input[name='action']");
    if(action){ action.value = "save_all"; }
}

function deleteOneRow(btn){
    const action = document.querySelector("input[name='action']");
    if(action){ action.value = "delete_one"; }
    return confirm("Xóa riêng dòng này?");
}

function deleteSelectedRows(){
    const action = document.querySelector("input[name='action']");
    const checked = document.querySelectorAll(".item-check:checked").length;

    if(checked === 0){
        alert("Bạn chưa chọn dòng nào để xóa.");
        return false;
    }

    if(action){ action.value = "delete_selected"; }
    return confirm("Xóa " + checked + " dòng đã chọn?");
}

function toggleRowLock(btn){
    const row = btn.closest("tr");
    row.classList.toggle("locked-row");
    const locked = row.classList.contains("locked-row");
    btn.textContent = locked ? "🔒 Khóa" : "🔓 Mở";
}

function toggleAllLocks(){
    const rows = document.querySelectorAll("#part1Table tbody tr");
    const hasUnlocked = Array.from(rows).some(row => !row.classList.contains("locked-row"));

    rows.forEach(row => {
        if(hasUnlocked){
            row.classList.add("locked-row");
            const btn = row.querySelector(".lock-btn");
            if(btn) btn.textContent = "🔒 Khóa";
        }else{
            row.classList.remove("locked-row");
            const btn = row.querySelector(".lock-btn");
            if(btn) btn.textContent = "🔓 Mở";
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
            row.style.display = text.includes(key) ? "" : "none";
        });
    });
}
</script>
</body>
</html>
''', encoding="utf-8")

print("DA_THEM_NUT_KHOA_VA_XOA_BEN_NGOAI_PART1")
