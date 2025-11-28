import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
APP = SRC / "app"
BACKUP = ROOT / "backup_phase2"
LOGFILE = ROOT / "refactor_phase2_log.txt"


def log(msg):
    print(msg)
    with open(LOGFILE, "a") as f:
        f.write(msg + "\n")


def safe_move(src, dst):
    """Move without overwriting; backup unexpected."""
    if not src.exists():
        return

    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists():
        backup_path = BACKUP / src.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(backup_path))
        log(f"[BACKUP] {src} → {backup_path}")
    else:
        shutil.move(str(src), str(dst))
        log(f"[MOVE] {src} → {dst}")


def delete_if_empty(path):
    if path.exists() and not any(path.iterdir()):
        shutil.rmtree(path)
        log(f"[DELETE EMPTY] {path}")


def main():
    log("=== STARTING PHASE 2 BACKEND REFACTOR ===")

    BACKUP.mkdir(exist_ok=True)

    # --------------------------------------------------------------------
    # 1. Move main.py → app/main.py
    # --------------------------------------------------------------------
    main_py = SRC / "main.py"
    safe_move(main_py, APP / "main.py")

    # --------------------------------------------------------------------
    # 2. Create infrastructure folder & move migrations
    # --------------------------------------------------------------------
    infra = APP / "infrastructure"
    infra.mkdir(exist_ok=True)
    migrations_src = SRC / "database" / "migrations"
    if migrations_src.exists():
        safe_move(migrations_src, infra / "migrations")

    # --------------------------------------------------------------------
    # 3. Move core files → app/core
    # --------------------------------------------------------------------
    core_src = SRC / "core"
    core_dst = APP / "core"

    core_dst.mkdir(exist_ok=True)

    core_files = ["config.py", "database.py"]
    for f in core_files:
        file_path = core_src / f
        safe_move(file_path, core_dst / f)

    # move base_repository to core
    base_repo = SRC / "services" / "base_repository.py"
    safe_move(base_repo, core_dst / "base_repository.py")

    # --------------------------------------------------------------------
    # 4. Move root api/router to app/api_router.py
    # --------------------------------------------------------------------
    old_routes = SRC / "api" / "routes.py"
    safe_move(old_routes, APP / "api_router.py")

    # --------------------------------------------------------------------
    # 5. Remove leftover folders (only if empty)
    # --------------------------------------------------------------------
    legacy_folders = [
        SRC / "models",
        SRC / "schemas",
        SRC / "services",
        SRC / "api",
        SRC / "core/security",
        SRC / "core",
        SRC / "database",
    ]

    for folder in legacy_folders:
        try:
            delete_if_empty(folder)
        except Exception as e:
            log(f"[SKIP DELETE] {folder} - Reason: {e}")

    # --------------------------------------------------------------------
    # 6. Sweep up any stray files in src/
    # --------------------------------------------------------------------
    for item in SRC.iterdir():
        if item.is_file():
            # Move to backup so nothing gets lost
            safe_move(item, BACKUP / item.name)

    log("=== PHASE 2 COMPLETE ===")


if __name__ == "__main__":
    if LOGFILE.exists():
        LOGFILE.unlink()
    main()
