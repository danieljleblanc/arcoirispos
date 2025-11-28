#!/usr/bin/env python3
import re
import sys
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# ------------------------------------------
# COMPLETE GLOBAL REWRITE MAP
# ------------------------------------------
REWRITE_MAP = {
    "src.core": "src.app.core",
    "src.inventory": "src.app.inventory",
    "src.pos": "src.app.pos",
    "src.org": "src.app.org",
    "src.auth": "src.app.auth",
    "src.accounting": "src.app.accounting",
    "src.infrastructure": "src.app.infrastructure",
    "src.models": "src.app",   # old invalid reference → correct root
}

# Match any "from src.xxx import ..." or "import src.xxx"
PATTERN = re.compile(r"(from|import)\s+(src\.[\w\.]+)")

def rewrite_line(line: str) -> str:
    match = PATTERN.search(line)
    if not match:
        return line

    prefix = match.group(1)
    module = match.group(2)

    for old, new in REWRITE_MAP.items():
        if module.startswith(old):
            fixed = line.replace(module, module.replace(old, new, 1))
            return fixed

    return line


def process_file(path: Path) -> bool:
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
        backup = path.with_suffix(".py.bak2")
        shutil.copy2(path, backup)
        path.write_text("".join(updated_lines))
        return True

    return False


def main():
    print("\n=== FIX IMPORTS v2: STARTING ===\n")

    modified = []

    for py in ROOT.rglob("*.py"):
        if "venv" in py.parts:
            continue
        if "__pycache__" in py.parts:
            continue
        if py.name.endswith(".py.bak") or py.name.endswith(".py.bak2"):
            continue

        if process_file(py):
            modified.append(str(py))

    print("\n=== FIX IMPORTS v2: COMPLETE ===")
    print(f"{len(modified)} files updated.\n")

    if modified:
        print("Updated files:")
        for f in modified:
            print("  -", f)
    else:
        print("No imports required updating.")


if __name__ == "__main__":
    main()
