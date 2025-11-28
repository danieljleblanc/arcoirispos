import sys
from pathlib import Path
import pkgutil, importlib, traceback, py_compile

# --------------------------------------------
# FIX: ensure "src/" is importable everywhere
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
# --------------------------------------------

REPORT = ROOT / "validation_report.txt"


# ------------------------------------------------------------
# FLEXIBLE PREFIX VALIDATION (correct rules)
# ------------------------------------------------------------
def has_invalid_prefix(line: str) -> bool:
    """
    VALID:
        from src.app.something import X
        from src.app import X
        import src.app.something
        import src.app

    INVALID:
        from src.core...
        from src.inventory...
        from src.pos...
        from src.org...
        import src.core...
        import src.inventory...
        import src.pos...
        import src.org...
    """

    line = line.strip()

    # Only scan import lines
    if not (line.startswith("from ") or line.startswith("import ")):
        return False

    # Allowed prefixes
    allowed_prefixes = (
        "from src.app",
        "import src.app",
    )
    if line.startswith(allowed_prefixes):
        return False

    # Forbidden prefixes
    forbidden_prefixes = (
        "from src.core",
        "from src.inventory",
        "from src.pos",
        "from src.org",
        "from src.api_router",  # must be src.app.api_router
        "import src.core",
        "import src.inventory",
        "import src.pos",
        "import src.org",
        "import src.api_router",
    )

    return line.startswith(forbidden_prefixes)


def assert_valid_imports():
    """
    Scan all files in src/ and reject any invalid prefixes.
    """
    bad_imports = []

    for pyfile in SRC.rglob("*.py"):
        if "__pycache__" in pyfile.parts:
            continue

        try:
            lines = pyfile.read_text(errors="ignore").splitlines()
        except:
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
            "\nAllowed imports must begin with: from src.app....\n"
        )


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


def import_all_modules():
    errors = []

    for importer, modname, ispkg in pkgutil.walk_packages(
        path=[str(SRC)],
        prefix="src."
    ):
        try:
            importlib.import_module(modname)
        except Exception as e:
            tb = traceback.format_exc()
            errors.append((modname, tb))

    return errors


def main():

    # New: prefix check BEFORE compiling/importing
    assert_valid_imports()

    if REPORT.exists():
        REPORT.unlink()

    print("\n=== PHASE 4: PROJECT VALIDATION STARTING ===\n")

    compile_errors = compile_all_py()
    import_errors = import_all_modules()

    with open(REPORT, "w") as f:
        if compile_errors:
            f.write("### PYTHON COMPILE ERRORS ###\n")
            for path, err in compile_errors:
                f.write(f"{path}\n  {err}\n\n")

        if import_errors:
            f.write("\n### IMPORT ERRORS ###\n")
            for mod, tb in import_errors:
                f.write(f"{mod}\n{tb}\n\n")

    print("\n=== PHASE 4 COMPLETE ===")
    print(f"Full report written to {REPORT}\n")

    if compile_errors or import_errors:
        print("❌ Problems detected — review validation_report.txt")
    else:
        print("✅ All modules validated successfully — no errors!")


if __name__ == "__main__":
    main()
