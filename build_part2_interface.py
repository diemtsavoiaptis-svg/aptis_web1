from pathlib import Path
import re

# ==================================================
# 1) Tạo template giao diện Part 2
# ==================================================
tpl = Path("templates/core/listening_part2.html")
tpl.parent.mkdir(parents=True, exist_ok=True)

tpl.write_text(r'''{% load static %}
<!doctype html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Listening Part 2 | Aptis</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet" href="{% static 'core/css/font_theme.css' %}">

    <style>
        :root {
            --red: #e60023;
            --red2: #ff5f76;
            --deep: #7a0010;
            --dark: #3f0011;
            --soft: #fff1f4;
            --soft2: #fff7f9;
            --line: #ffd1dc;
            --muted: #667085;
            --white: #ffffff;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            background:
                radial-gradient(circle at top right, rgba(255, 95, 118, .18), transparent 34%),
                linear-gradient(135deg, #fffafa 0%, #fff0f4 48%, #fff7f9 100%);
            color: var(--dark);
            font-family: "Segoe UI", Tahoma, Arial, sans-serif;
        }

        .part2-page {
            max-width: 1240px;
            margin: 0 auto;
            padding: 26px 20px 34px;
        }

        .part2-topbar {
            border-left: 4px solid var(--red);
            background: linear-gradient(90deg, #fff1f4, #fff7f9);
            border-radius: 0 12px 12px 0;
            padding: 14px 18px;
            font-weight: 900;
            color: var(--deep);
            box-shadow: 0 10px 24px rgba(180, 0, 30, .06);
        }

        .topic-card {
            margin-top: 16px;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 18px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: rgba(255, 255, 255, .9);
            color: var(--dark);
            box-shadow: 0 12px 28px rgba(180, 0, 30, .06);
        }

        .topic-card .label {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: var(--deep);
            font-weight: 950;
            text-transform: uppercase;
            letter-spacing: .04em;
            font-size: 14px;
        }

        .topic-card .topic-text {
            font-weight: 850;
            font-size: 17px;
        }

        .answer-pool {
            margin-top: 18px;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(255,255,255,.92);
            box-shadow: 0 18px 40px rgba(180, 0, 30, .06);
            overflow: hidden;
        }

        .pool-head {
            padding: 15px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            color: var(--deep);
            font-weight: 950;
            border-bottom: 1px solid #ffe1e7;
        }

        .pool-head small {
            color: var(--muted);
            font-weight: 700;
        }

        .pool-grid {
            padding: 14px 16px;
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
        }

        .pool-option {
            min-height: 48px;
            padding: 11px 13px;
            border-radius: 12px;
            border: 1px solid #f7c6cf;
            background: #fffafa;
            color: var(--dark);
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 750;
        }

        .choice-letter {
            width: 24px;
            height: 24px;
            flex: 0 0 24px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background: white;
            border: 1px solid #f2aeb9;
            color: var(--deep);
            font-size: 13px;
            font-weight: 950;
        }

        .voice-list {
            margin-top: 16px;
            display: grid;
            gap: 12px;
        }

        .voice-card {
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(255,255,255,.94);
            box-shadow: 0 16px 38px rgba(180, 0, 30, .055);
            padding: 17px 18px;
            display: grid;
            grid-template-columns: 1fr 176px;
            gap: 14px;
            align-items: center;
        }

        .voice-info {
            display: grid;
            grid-template-columns: 42px 1fr;
            gap: 14px;
            align-items: start;
        }

        .number-badge {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, var(--red), var(--red2));
            color: white;
            font-weight: 950;
            box-shadow: 0 12px 22px rgba(230, 0, 35, .16);
        }

        .voice-kicker {
            color: var(--muted);
            font-size: 13px;
            text-transform: uppercase;
            font-weight: 900;
            letter-spacing: .04em;
        }

        .voice-title {
            margin-top: 3px;
            font-size: 20px;
            font-weight: 950;
            color: var(--dark);
        }

        .audio-row {
            margin-top: 12px;
            min-height: 66px;
            border-radius: 14px;
            background: #fff1f4;
            border: 1px solid #ffe1e7;
            display: grid;
            grid-template-columns: 52px 1fr 34px;
            align-items: center;
            gap: 12px;
            padding: 12px 14px;
        }

        .play-btn {
            width: 40px;
            height: 40px;
            border: 0;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--red), var(--red2));
            color: white;
            font-size: 15px;
            font-weight: 950;
            cursor: pointer;
            display: grid;
            place-items: center;
            box-shadow: 0 12px 20px rgba(230, 0, 35, .17);
        }

        .fake-audio {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #7a0010;
            font-weight: 800;
        }

        .bar {
            height: 4px;
            flex: 1;
            border-radius: 999px;
            background: #f2c6ce;
            position: relative;
            overflow: hidden;
        }

        .bar::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: var(--progress, 25%);
            border-radius: inherit;
            background: linear-gradient(90deg, var(--red), var(--red2));
        }

        .speaker-icon {
            color: var(--deep);
            opacity: .78;
        }

        .answer-select {
            width: 100%;
            height: 48px;
            border-radius: 14px;
            border: 1px dashed #f0aeb8;
            background: white;
            color: var(--muted);
            padding: 0 13px;
            font-size: 15px;
            font-weight: 750;
            outline: none;
            cursor: pointer;
        }

        .answer-select:focus {
            border-color: var(--red);
            box-shadow: 0 0 0 4px rgba(230,0,35,.10);
            color: var(--dark);
        }

        .flag-btn {
            justify-self: end;
            width: 34px;
            height: 34px;
            border-radius: 50%;
            border: 1px solid #ffe1e7;
            background: white;
            color: #d0001e;
            cursor: pointer;
            font-size: 16px;
        }

        .voice-actions {
            display: grid;
            grid-template-columns: 1fr 34px;
            gap: 10px;
            align-items: center;
        }

        .bottom-actions {
            margin-top: 14px;
            padding-top: 14px;
            border-top: 1px solid #ffe1e7;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }

        .btn {
            min-width: 128px;
            height: 52px;
            border-radius: 12px;
            border: 0;
            padding: 0 22px;
            font-size: 17px;
            font-weight: 950;
            cursor: pointer;
            font-family: inherit;
        }

        .btn-ghost {
            background: white;
            border: 1px solid #d8dfea;
            color: #98a2b3;
        }

        .btn-next {
            background: #b56b76;
            color: white;
        }

        .btn-submit {
            background: linear-gradient(135deg, var(--red), var(--red2));
            color: white;
            box-shadow: 0 14px 28px rgba(230,0,35,.18);
        }

        .note-card {
            margin-top: 12px;
            border: 1px solid #ffe1e7;
            border-radius: 16px;
            padding: 13px 15px;
            color: #8a0015;
            background: #fffafa;
            font-weight: 750;
            line-height: 1.55;
        }

        @media (max-width: 900px) {
            .pool-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .voice-card {
                grid-template-columns: 1fr;
            }

            .voice-actions {
                grid-template-columns: 1fr;
            }

            .flag-btn {
                justify-self: start;
            }

            .bottom-actions {
                flex-wrap: wrap;
            }

            .btn {
                flex: 1;
            }
        }

        @media (max-width: 560px) {
            .pool-grid {
                grid-template-columns: 1fr;
            }

            .part2-page {
                padding: 18px 12px 28px;
            }

            .topic-card {
                border-radius: 16px;
                align-items: flex-start;
                flex-direction: column;
            }
        }
    </style>
</head>

<body>
    <main class="part2-page">
        <section class="part2-topbar">
            Part 2
        </section>

        <section class="topic-card">
            <span class="label">🏷 Topic</span>
            <span class="topic-text">When they like listening to music</span>
        </section>

        <section class="answer-pool">
            <div class="pool-head">
                <div>☰ Pool đáp án</div>
                <small>Mỗi đáp án đúng 1 lần</small>
            </div>

            <div class="pool-grid">
                <div class="pool-option"><span class="choice-letter">A</span> To relax</div>
                <div class="pool-option"><span class="choice-letter">B</span> While studying</div>
                <div class="pool-option"><span class="choice-letter">C</span> While singing</div>
                <div class="pool-option"><span class="choice-letter">D</span> After waking up</div>
            </div>
        </section>

        <section class="voice-list">
            <article class="voice-card">
                <div class="voice-info">
                    <div class="number-badge">1</div>
                    <div>
                        <div class="voice-kicker">Câu 1 / 4</div>
                        <div class="voice-title">Câu 1</div>

                        <div class="audio-row">
                            <button class="play-btn" type="button">▶</button>
                            <div class="fake-audio">
                                <span>0:29 / 0:29</span>
                                <div class="bar" style="--progress: 100%"></div>
                            </div>
                            <div class="speaker-icon">🔊</div>
                        </div>
                    </div>
                </div>

                <div class="voice-actions">
                    <select class="answer-select">
                        <option>Chọn đáp án...</option>
                        <option>A - To relax</option>
                        <option>B - While studying</option>
                        <option>C - While singing</option>
                        <option>D - After waking up</option>
                    </select>
                    <button class="flag-btn" type="button">⚐</button>
                </div>
            </article>

            <article class="voice-card">
                <div class="voice-info">
                    <div class="number-badge">2</div>
                    <div>
                        <div class="voice-kicker">Câu 2 / 4</div>
                        <div class="voice-title">Câu 2</div>

                        <div class="audio-row">
                            <button class="play-btn" type="button">▶</button>
                            <div class="fake-audio">
                                <span>0:19 / 0:25</span>
                                <div class="bar" style="--progress: 72%"></div>
                            </div>
                            <div class="speaker-icon">🔊</div>
                        </div>
                    </div>
                </div>

                <div class="voice-actions">
                    <select class="answer-select">
                        <option>Chọn đáp án...</option>
                        <option>A - To relax</option>
                        <option>B - While studying</option>
                        <option>C - While singing</option>
                        <option>D - After waking up</option>
                    </select>
                    <button class="flag-btn" type="button">⚐</button>
                </div>
            </article>

            <article class="voice-card">
                <div class="voice-info">
                    <div class="number-badge">3</div>
                    <div>
                        <div class="voice-kicker">Câu 3 / 4</div>
                        <div class="voice-title">Câu 3</div>

                        <div class="audio-row">
                            <button class="play-btn" type="button">▶</button>
                            <div class="fake-audio">
                                <span>0:01 / 0:24</span>
                                <div class="bar" style="--progress: 8%"></div>
                            </div>
                            <div class="speaker-icon">🔊</div>
                        </div>
                    </div>
                </div>

                <div class="voice-actions">
                    <select class="answer-select">
                        <option>Chọn đáp án...</option>
                        <option>A - To relax</option>
                        <option>B - While studying</option>
                        <option>C - While singing</option>
                        <option>D - After waking up</option>
                    </select>
                    <button class="flag-btn" type="button">⚐</button>
                </div>
            </article>

            <article class="voice-card">
                <div class="voice-info">
                    <div class="number-badge">4</div>
                    <div>
                        <div class="voice-kicker">Câu 4 / 4</div>
                        <div class="voice-title">Câu 4</div>

                        <div class="audio-row">
                            <button class="play-btn" type="button">▶</button>
                            <div class="fake-audio">
                                <span>0:23 / 0:23</span>
                                <div class="bar" style="--progress: 100%"></div>
                            </div>
                            <div class="speaker-icon">🔊</div>
                        </div>
                    </div>
                </div>

                <div class="voice-actions">
                    <select class="answer-select">
                        <option>Chọn đáp án...</option>
                        <option>A - To relax</option>
                        <option>B - While studying</option>
                        <option>C - While singing</option>
                        <option>D - After waking up</option>
                    </select>
                    <button class="flag-btn" type="button">⚐</button>
                </div>
            </article>
        </section>

        <div class="note-card">
            Đây là bản bố cục giao diện Part 2. Dữ liệu thật như topic, audio, đáp án và transcript sẽ được nối sau khi mình tạo phần quản lý dữ liệu Part 2.
        </div>

        <section class="bottom-actions">
            <button class="btn btn-ghost" type="button">Previous Part</button>
            <button class="btn btn-next" type="button">Next Part</button>
            <button class="btn btn-submit" type="button">Submit</button>
        </section>
    </main>

    <script>
        // Mỗi đáp án chỉ được chọn 1 lần trên 4 câu.
        const selects = Array.from(document.querySelectorAll(".answer-select"));

        function refreshOptions() {
            const chosen = selects
                .map(s => s.value)
                .filter(v => v && v !== "Chọn đáp án...");

            selects.forEach(select => {
                Array.from(select.options).forEach(opt => {
                    if (!opt.value || opt.value === "Chọn đáp án...") return;
                    opt.disabled = chosen.includes(opt.value) && select.value !== opt.value;
                });
            });
        }

        selects.forEach(s => s.addEventListener("change", refreshOptions));
    </script>
</body>
</html>
''', encoding="utf-8")


# ==================================================
# 2) Thêm view Part 2 nếu chưa có
# ==================================================
views = Path("core/views.py")
s = views.read_text(encoding="utf-8", errors="ignore")

if "def admin_part2_questions(request):" not in s:
    s += r'''

# ===== Listening Part 2 preview/interface =====
def admin_part2_questions(request):
    return render(request, "core/listening_part2.html")
# ===== End Listening Part 2 preview/interface =====
'''
    views.write_text(s, encoding="utf-8")


# ==================================================
# 3) Thêm URL /dashboard/part-2/
# ==================================================
urls = Path("core/urls.py")
u = urls.read_text(encoding="utf-8", errors="ignore")

if 'dashboard/part-2/' not in u:
    u = re.sub(
        r"urlpatterns\s*=\s*\[",
        'urlpatterns = [\n    path("dashboard/part-2/", views.admin_part2_questions, name="admin_part2_questions"),',
        u,
        count=1
    )

urls.write_text(u, encoding="utf-8")


# ==================================================
# 4) Cập nhật dashboard/listening-parts để nút Part 2 mở được nếu có
# ==================================================
for p in [Path("templates/core/dashboard.html"), Path("templates/core/listening_parts.html")]:
    if not p.exists():
        continue

    d = p.read_text(encoding="utf-8", errors="ignore")
    old = d

    d = d.replace('data-url="/admin/core/lesson/"', 'data-url="/admin/core/lesson/"')
    d = d.replace('href="/dashboard/part-2/"', 'href="/dashboard/part-2/"')

    # Nếu template có chữ Sắp mở gần Part 2 thì đổi thành mở Part 2 theo cách nhẹ, không phá Part 1.
    d = d.replace("Sẽ thiết kế sau khi hoàn thiện Part 1.", "Bố cục Part 2: 1 topic lớn, 4 voice thảo luận, chọn đáp án từ pool A-D.")
    d = d.replace("Sắp mở", "Mở Part 2")
    d = d.replace("Sẵn sàng thiết kế", "Đã có bố cục")

    if old != d:
        p.write_text(d, encoding="utf-8")

print("DA_TAO_GIAO_DIEN_PART2_THEO_BO_CUC_MAU")
