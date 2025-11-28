#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# -------------------------------------------------------------------
# Patterns for INVALID imports that must be corrected
# -------------------------------------------------------------------

INVALID_IMPORTS = [
    # from src.core...
    (r"from\s+src\.core(?:\.|s\b)", "from src.app.core"),
    (r"import\s+src\.core(?:\.|s\b)", "import src.app.core"),

    # from src.inventory...
    (r"from\s+src\.inventory", "from src.app.inventory"),
    (r"import\s+src\.inventory", "import src.app.inventory"),

    # from src.pos...
    (r"from\s+src\.pos", "from src.app.pos"),
    (r"import\s+src\.pos", "import src.app.pos"),

    # from src.org...
    (r"from\s+src\.org", "from src.app.org"),
    (r"import\s+src\.org", "import src.app.org"),

    # from src.auth...
    (r"from\s+src\.auth", "from src.app.auth"),
    (r"import\s+src\.auth", "import src.app.auth"),

    # src.api_router (incorrect root)
    (r"from\s+src\.api_router", "from src.app.api_router"),
    (r"import\s+src\.api_router", "import src.app.api_router"),
]


# -------------------------------------------------------------------
# Helper function that applies fixes to a single file
# -------------------------------------------------------------------
def fix_file(path: Path) -> bool:
    original = path.read_text(errors="ignore")
    updated = original

    for pattern, replacement in INVALID_IMPORTS:
        updated = re.sub(pattern, replacement, updated)

    if updated != original:
        path.write_text(updated)
        return True

    return False


# -------------------------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------------------------
def main():
    print("\n=== FIX IMPORTS v3: STARTING ===\n")

    modified = []

    for pyfile in SRC.rglob("*.py"):
        if "__pycache__" in pyfile.parts:
            continue
        if "backup_" in pyfile.parts:
            continue

        if fix_file(pyfile):
            modified.append(str(pyfile))

    print("\n=== FIX IMPORTS v3: COMPLETE ===")
    print(f"{len(modified)} files updated.\n")

    if modified:
        print("Updated files:")
        for m in modified:
            print("  -", m)
    else:
        print("No changes needed — all imports already valid!\n")


if __name__ == "__main__":
    main()
