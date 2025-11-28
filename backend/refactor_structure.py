import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
APP = SRC / "app"

LOGFILE = ROOT / "refactor_log.txt"
BACKUP = ROOT / "backup_unexpected"

# Domain folders to create
DOMAINS = [
    "auth",
    "pos",
    "inventory",
    "accounting",
    "org",
]

def log(msg):
    print(msg)
    with open(LOGFILE, "a") as f:
        f.write(msg + "\n")


def safe_move(src, dst):
    """Move file without overwriting; backup unexpected files."""
    dst.parent.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        return

    if dst.exists():
        backup_path = BACKUP / src.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(backup_path))
        log(f"[BACKUP] {src} → {backup_path} (dst exists)")
    else:
        shutil.move(str(src), str(dst))
        log(f"[MOVE] {src} → {dst}")


def delete_if_exists(path):
    if path.exists():
        shutil.rmtree(path)
        log(f"[DELETE] {path}")


def main():
    log("=== Starting Project Structure Refactor ===")

    # 1. Create new src/app domain structure
    for folder in DOMAINS:
        domain_path = APP / folder / "models"
        (APP / folder / "schemas").mkdir(parents=True, exist_ok=True)
        (APP / folder / "services").mkdir(parents=True, exist_ok=True)
        (APP / folder / "routes").mkdir(parents=True, exist_ok=True)
        domain_path.mkdir(parents=True, exist_ok=True)
        log(f"[CREATE] Domain folder created: {domain_path}")

    # 2. Move models into new domain structure
    MODEL_MAP = {
        "pos": SRC / "models" / "pos",
        "inventory": SRC / "models" / "inv",
        "accounting": SRC / "models" / "acct",
        "org": SRC / "models" / "core",
    }

    for domain, old_path in MODEL_MAP.items():
        if old_path.exists():
            for file in old_path.glob("*.py"):
                safe_move(file, APP / domain / "models" / file.name)

    # 3. Move schemas
    SCHEMA_MAP = {
        "pos": SRC / "schemas" / "pos_schemas.py",
        "inventory": SRC / "schemas" / "inv_schemas.py",
        "accounting": SRC / "schemas" / "acct_schemas.py",
        "org": SRC / "schemas" / "core_schemas.py",
    }

    for domain, file_path in SCHEMA_MAP.items():
        if file_path.exists():
            safe_move(file_path, APP / domain / "schemas" / file_path.name)

    # 4. Move services
    SERVICE_MAP = {
        "pos": SRC / "services" / "pos",
        "inventory": SRC / "services" / "inv",
        "accounting": SRC / "services" / "acct",
        "org": SRC / "services" / "core",
    }

    for domain, old_path in SERVICE_MAP.items():
        if old_path.exists():
            for file in old_path.glob("*.py"):
                safe_move(file, APP / domain / "services" / file.name)

    # 5. Move routes
    ROUTE_MAP = SRC / "api"

    for file in ROUTE_MAP.glob("*_routes.py"):
        name = file.name.replace("_routes.py", "")
        if name.startswith("sale") or name.startswith("sales") or "payment" in name:
            safe_move(file, APP / "pos" / "routes" / file.name)
        elif "item" in name or "stock" in name or "location" in name:
            safe_move(file, APP / "inventory" / "routes" / file.name)
        elif "tax" in name or "terminal" in name or "customer" in name:
            safe_move(file, APP / "pos" / "routes" / file.name)
        elif "auth" in name:
            safe_move(file, APP / "auth" / "routes" / file.name)
        else:
            safe_move(file, BACKUP / "routes_misc" / file.name)

    # 6. Move authentication & security to app/auth
    SECURITY_FILES = [
        "auth.py", "dependencies.py", "hashing.py",
        "jwt_utils.py", "permissions.py", "roles.py",
        "schemas.py", "security.py"
    ]

    for fname in SECURITY_FILES:
        src = SRC / "core" / "security" / fname
        dst = APP / "auth" / ("services" if fname.endswith(".py") else "misc") / fname
        if src.exists():
            safe_move(src, dst)

    # 7. Move organization models/services/routes into app/org
    ORG_SRC = SRC / "models" / "core"
    if ORG_SRC.exists():
        for file in ORG_SRC.glob("*.py"):
            safe_move(file, APP / "org" / "models" / file.name)

    # 8. Clean dead folders
    dead_paths = [
        SRC / "models_old",
        SRC / "schemas_old",
        SRC / "services_old",
        SRC / "__pycache__",
    ]

    for path in dead_paths:
        delete_if_exists(path)

    # Remove pycache everywhere
    for pycache in SRC.rglob("__pycache__"):
        delete_if_exists(pycache)

    log("=== Refactor Completed ===")


if __name__ == "__main__":
    BACKUP.mkdir(exist_ok=True)
    LOGFILE.unlink(missing_ok=True)
    main()
