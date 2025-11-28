#!/usr/bin/env python3
import re
import sys
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# ------------------------------------------
# MAPPING: OLD → NEW namespace
# ------------------------------------------
REWRITE_MAP = {
    "src.core": "src.app.core",
    "src.inventory": "src.app.inventory",
    "src.pos": "src.app.pos",
    "src.org": "src.app.org",
    "src.accounting": "src.app.accounting",
    "src.auth": "src.app.auth",
    "src.infrastructure": "src.app.infrastructure",
}

# Regex patterns for imports
PATTERNS = [
    # from src.xxx import YYY
    re.compile(r"^(from\s+)(src\.[A-Za-z0-9_\.]+)(\s+import\s+.+)$"),
    # import src.xxx.yyy
    re.compile(r"^(import\s+)(src\.[A-Za-z0-9_\.]+)$"),
]


def rewrite_line(line: str):
    """Rewrite a single import line based on REWRITE_MAP rules."""
    for pattern in PATTERNS:
        m = pattern.match(line)
        if m:
            prefix, module, suffix = m.groups() if len(m.groups()) == 3 else (m.group(1), m.group(2), "")
            for old, new in REWRITE_MAP.items():
                if module.startswith(old):
                    updated = prefix + module.replace(old, new, 1) + suffix
                    return updated
    return line


def process_file(path: Path):
    """Rewrite imports inside one file, creating a backup if changes occur."""
    original = path.read_text()
    lines = original.splitlines(True)
    updated_lines = []
    changed = False

    for line in lines:
        new_line = rewrite_line(line)
        if new_line != line:
            changed = True
        updated_lines.append(new_line)

    if changed:
        backup = path.with_suffix(".py.bak")
        shutil.copy2(path, backup)
        path.write_text("".join(updated_lines))
        return True
    return False


def main():
    print("\n=== FIX IMPORTS: STARTING ===\n")

    modified = []

    for py in ROOT.rglob("*.py"):
        if "venv" in py.parts:
            continue
        if "__pycache__" in py.parts:
            continue
        if py.name.endswith(".py.bak"):
            continue

        if process_file(py):
            modified.append(str(py))

    print("\n=== FIX IMPORTS: COMPLETE ===")
    print(f"{len(modified)} files updated.\n")

    if modified:
        print("Modified files:")
        for f in modified:
            print("  -", f)
    else:
        print("No changes needed — all imports already correct.")


if __name__ == "__main__":
    main()
