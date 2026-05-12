from pathlib import Path

tpl = Path("templates/core/admin_part4_questions.html")
html = tpl.read_text(encoding="utf-8-sig")

html = html.replace(
    ".col-audio { width: 230px; }",
    ".col-audio { width: 420px; }"
)

html = html.replace(
    "min-width: 1780px;",
    "min-width: 2200px;"
)

old = '''<input name="audio_url_{{ row.material.id }}" value="{{ row.material.audio_url }}" placeholder="https://...">'''

new = '''<textarea class="audio-url-area" name="audio_url_{{ row.material.id }}" placeholder="Paste audio URL here">{{ row.material.audio_url }}</textarea>
{% if row.material.audio_url %}
    <div class="audio-url-preview">URL saved</div>
{% else %}
    <div class="audio-url-missing">Missing URL</div>
{% endif %}'''

if old not in html:
    print("Audio input pattern not found. It may already be changed.")
else:
    html = html.replace(old, new)

extra_css = '''
<style id="audio-url-admin-fix">
.audio-url-area {
    min-height: 96px !important;
    width: 100% !important;
    font-size: 13px !important;
    line-height: 1.45 !important;
    word-break: break-all !important;
    white-space: pre-wrap !important;
}
.audio-url-preview {
    margin-top: 8px;
    color: #0f7a32;
    font-weight: 900;
    font-size: 12px;
}
.audio-url-missing {
    margin-top: 8px;
    color: #b00020;
    font-weight: 900;
    font-size: 12px;
}
</style>
'''

if 'id="audio-url-admin-fix"' not in html:
    html = html.replace("</head>", extra_css + "\n</head>")

tpl.write_text(html, encoding="utf-8")
print("Done: Part 4 admin audio URL field is now wider and shows full saved URL.")
