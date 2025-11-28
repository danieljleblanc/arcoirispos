import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

BACKUP = ROOT / "backup_final_imports"
BACKUP.mkdir(exist_ok=True)


# ----------------------------------------------------
# OLD → NEW mapping rules
# ----------------------------------------------------
REWRITE_MAP = {

    # ---- CORE ----
    r"\bsrc\.core\.config\b": "app.core.config",
    r"\bsrc\.core\.database\b": "app.core.database",
    r"\bsrc\.core\.security\.(\w+)": r"app.auth.services.\1",

    # ---- BASE ----
    r"\bsrc\.models\.base\b": "app.core.base",
    r"\bmodels\.base\b": "app.core.base",
    r"\bsrc\.services\.base_repository\b": "app.core.base_repository",
    r"\bservices\.base_repository\b": "app.core.base_repository",

    # ---- DOMAIN MODELS ----
    r"\bsrc\.models\.pos\.(\w+)": r"app.pos.models.\1",
    r"\bpos\.(\w+)": r"app.pos.models.\1",

    r"\bsrc\.models\.inv\.(\w+)": r"app.inventory.models.\1",
    r"\binv\.(\w+)": r"app.inventory.models.\1",

    r"\bsrc\.models\.acct\.(\w+)": r"app.accounting.models.\1",
    r"\bacct\.(\w+)": r"app.accounting.models.\1",

    r"\bsrc\.models\.core\.(\w+)": r"app.org.models.\1",
    r"\bcore\.(organization_models|role_models|user_models)\b": r"app.org.models.\1",

    # ---- DOMAIN SCHEMAS ----
    r"\bsrc\.schemas\.pos_schemas\b": "app.pos.schemas.pos_schemas",
    r"\bsrc\.schemas\.inv_schemas\b": "app.inventory.schemas.inv_schemas",
    r"\bsrc\.schemas\.acct_schemas\b": "app.accounting.schemas.acct_schemas",

    # ---- DOMAIN SERVICES ----
    r"\bsrc\.services\.pos\.(\w+)": r"app.pos.services.\1",
    r"\bsrc\.services\.inv\.(\w+)": r"app.inventory.services.\1",
    r"\bsrc\.services\.acct\.(\w+)": r"app.accounting.services.\1",
    r"\bsrc\.services\.core\.(\w+)": r"app.org.services.\1",

    # ---- ROUTES ----
    r"\bsrc\.api\.routes\b": "app.api_router",

    # ---- GENERIC src.models → app.*
    r"\bsrc\.models\b": "app",

    # ---- RANDOM OLD PATTERNS ----
    r"\bsrc\.schemas\b": "app",
    r"\bsrc\.services\b": "app",
    r"\bmodels\.(\w+)": r"app.\1.models",
}


# ----------------------------------------------------
# Apply rewrite rules to text
# ----------------------------------------------------
def rewrite_imports(text: str) -> str:
    for old, new in REWRITE_MAP.items():
        text = re.sub(old, new, text)
    return text


# ----------------------------------------------------
# Process all .py files under src/
# ----------------------------------------------------
def process_file(path: Path):
    rel = path.relative_to(SRC)
    backup_path = BACKUP / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    original = path.read_text(encoding="utf-8")

    new_text = rewrite_imports(original)

    if new_text != original:
        # backup original
        shutil.copy2(path, backup_path)
        # write updated
        path.write_text(new_text, encoding="utf-8")
        print(f"[FIXED] {path}")
    else:
        print(f"[NOCHANGE] {path}")


def main():
    print("\n=== STARTING FULL IMPORT REWRITE (PHASE 3C) ===\n")

    for py in SRC.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        if "backup_" in py.parts:
            continue
        process_file(py)

    print("\n=== IMPORT REWRITE COMPLETE ===")
    print(f"Backups saved under: {BACKUP}\n")


if __name__ == "__main__":
    main()
