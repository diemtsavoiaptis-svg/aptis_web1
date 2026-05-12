from pathlib import Path
import shutil

print("=== RESTORE FROM LATEST LESSON UI BACKUP ===")

backup_dirs = sorted(Path("code_backups").glob("before_remove_lesson_management_ui_*"))

if not backup_dirs:
    print("Không tìm thấy backup before_remove_lesson_management_ui_*")
    raise SystemExit(1)

latest = backup_dirs[-1]
print("Restoring from:", latest)

# Restore templates
src_templates = latest / "templates"
if src_templates.exists():
    if Path("templates").exists():
        shutil.rmtree("templates")
    shutil.copytree(src_templates, "templates")
    print("Restored templates")

# Restore core
src_core = latest / "core"
if src_core.exists():
    if Path("core").exists():
        shutil.rmtree("core")
    shutil.copytree(src_core, "core")
    print("Restored core")

print("DONE RESTORE")
