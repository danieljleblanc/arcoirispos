# backend/validate_project.py
"""
Project Code Health Validator
ArcoirisPOS Backend
---------------------------------------------

Validates:
1. Correct import prefixes (must begin with src.app.*)
2. Python compilation checks
3. Importing all backend modules safely
4. Ensures no legacy incorrect imports
5. Writes a full validation report

Run with:
    python validate_project.py
"""

import sys
from pathlib import Path
import pkgutil
import importlib
import traceback
import py_compile

# --------------------------------------------
# Correct project ROOT and SRC paths
# --------------------------------------------
ROOT = Path(__file__).resolve().parent        # backend/
SRC = ROOT / "src" / "app"                    # backend/src/app

if str(SRC.parent) not in sys.path:
    sys.path.insert(0, str(SRC.parent))
# --------------------------------------------

REPORT = ROOT / "validation_report.txt"


# ------------------------------------------------------------
# Updated Import Prefix Policy
# ------------------------------------------------------------
def has_invalid_prefix(line: str) -> bool:
    """
    VALID:
        from src.app.<module> import X
        import src.app.<module>
    
    INVALID:
        from src.<something_without_app>
        import src.<something_without_app>
        Legacy patterns: src.core.*, src.inventory.*, src.pos.*, src.org.*

    This enforces consistency after the 2025-11-30 architectural cleanup.
    """

    line = line.strip()

    # Only analyze import lines
    if not (line.startswith("from ") or line.startswith("import ")):
        return False

    # Allowed prefixes
    allowed_prefixes = (
        "from src.app",
        "import src.app",
    )
    if line.startswith(allowed_prefixes):
        return False

    # Forbidden (legacy) prefixes
    forbidden_prefixes = (
        "from src.core",
        "from src.inventory",
        "from src.pos",
        "from src.org",
        "from src.api_router",
        "import src.core",
        "import src.inventory",
        "import src.pos",
        "import src.org",
        "import src.api_router",
    )

    return line.startswith(forbidden_prefixes)


def assert_valid_imports():
    """
    Scan all backend/src/app/ files for invalid imports.
    """
    bad_imports = []

    for pyfile in SRC.rglob("*.py"):
        if "__pycache__" in pyfile.parts:
            continue

        try:
            lines = pyfile.read_text(errors="ignore").splitlines()
        except Exception:
            continue

        for i, line in enumerate(lines, start=1):
            if has_invalid_prefix(line):
                bad_imports.append((pyfile, i, line.strip()))

    if bad_imports:
        print("\n❌ INVALID IMPORT PREFIXES DETECTED:")
        for filepath, lineno, text in bad_imports:
            print(f"  {filepath}:{lineno}   (bad import: {text})")

        raise SystemExit(
            "\nSTOPPED: Fix invalid import paths before continuing."
            "\nAll imports must begin with: from src.app... or import src.app...\n"
        )


# ------------------------------------------------------------
# Standard compilation check
# ------------------------------------------------------------
def compile_all_py():
    errors = []
    for py in ROOT.rglob("*.py"):
        if "backup_" in py.parts:
            continue
        if "__pycache__" in py.parts:
            continue
        try:
            py_compile.compile(str(py), doraise=True)
        except Exception as e:
            errors.append((str(py), str(e)))
    return errors


# ------------------------------------------------------------
# Attempt to import all src.app modules
# ------------------------------------------------------------
def import_all_modules():
    errors = []

    pkg_base = str(SRC.parent.resolve())  # backend/src
    if pkg_base not in sys.path:
        sys.path.insert(0, pkg_base)

    for _, modname, ispkg in pkgutil.walk_packages(
        path=[str(SRC.parent)],
        prefix="src.app."
    ):
        try:
            importlib.import_module(modname)
        except Exception:
            tb = traceback.format_exc()
            errors.append((modname, tb))

    return errors


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():

    # 1. Prefix checks
    assert_valid_imports()

    # Remove old report
    if REPORT.exists():
        REPORT.unlink()

    print("\n=== PHASE 4: PROJECT CODE VALIDATION STARTING ===\n")

    # 2. Compile check
    compile_errors = compile_all_py()

    # 3. Import check
    import_errors = import_all_modules()

    # 4. Write report
    with open(REPORT, "w") as f:
        if compile_errors:
            f.write("### PYTHON COMPILE ERRORS ###\n")
