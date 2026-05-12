from pathlib import Path

views = Path("core/views.py")
text = views.read_text(encoding="utf-8-sig")

patch = r'''

# === FIX PART 4 GOOGLE DRIVE AUDIO STREAM START ===
@login_required
def secure_part4_audio_view(request, material_id):
    material = get_object_or_404(ListeningPartMaterial, id=material_id, part=4)

    audio_url = (getattr(material, "audio_url", "") or "").strip()

    if not audio_url:
        raise Http404("Audio không tồn tại.")

    drive_file_id = extract_drive_file_id(audio_url)

    if drive_file_id:
        return _google_drive_download_response(drive_file_id)

    response = HttpResponseRedirect(audio_url)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
# === FIX PART 4 GOOGLE DRIVE AUDIO STREAM END ===
'''

start = "# === FIX PART 4 GOOGLE DRIVE AUDIO STREAM START ==="
end = "# === FIX PART 4 GOOGLE DRIVE AUDIO STREAM END ==="

if start in text and end in text:
    before = text.split(start)[0].rstrip()
    after = text.split(end, 1)[1].lstrip()
    text = before + "\n" + patch + "\n" + after
else:
    text = text.rstrip() + "\n" + patch + "\n"

views.write_text(text, encoding="utf-8")


tpl = Path("templates/core/student_part4.html")
html = tpl.read_text(encoding="utf-8-sig")

html = html.replace(
    'src="{{ selected.audio_url }}"',
    'src="{% url \'secure_part4_audio\' selected.id %}"'
)

tpl.write_text(html, encoding="utf-8")

print("Fixed Part 4 audio: Google Drive links now stream through /secure/part4-audio/<id>/")
