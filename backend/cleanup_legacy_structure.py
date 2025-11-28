from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

LEGACY_FOLDERS = [
    "api",
    "core",
    "models",
    "schemas",
    "services",
]

ARCHIVE_DIR = ROOT / "legacy_archives"
ARCHIVE_DIR.mkdir(exist_ok=True)

print("\n=== STARTING SAFE LEGACY CLEANUP ===\n")
print(f"Archiving to: {ARCHIVE_DIR}\n")

moved = []

for folder_name in LEGACY_FOLDERS:
    folder_path = SRC / folder_name

    if not folder_path.exists():
        print(f"[SKIP] {folder_path} does not exist, OK")
        continue

    # The new structure lives only under src/app/
    if folder_name == "core" and (SRC / "app" / "core").exists():
        print(f"[ARCHIVE] Legacy core/ found — will archive")
    elif folder_name in ["models", "schemas", "services", "api"]:
        print(f"[ARCHIVE] Legacy {folder_name}/ found — will archive")

    target = ARCHIVE_DIR / folder_name
    if target.exists():
        print(f"[WARN] Archive target already exists: {target} — making unique copy")
        target = ARCHIVE_DIR / f"{folder_name}_archive"

    shutil.move(str(folder_path), str(target))
    moved.append((folder_path, target))
    print(f"[MOVED] {folder_path} → {target}")

print("\n=== CLEANUP COMPLETE ===\n")

if moved:
    print("Moved folders:")
    for old, new in moved:
        print(f"  {old} → {new}")

else:
    print("No legacy folders were found — nothing moved.")

print("\nYou may now re-run: python3 validate_project.py\n")
