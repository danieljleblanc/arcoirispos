import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

REPORT = ROOT / "import_report.txt"

EXCLUDE_DIRS = {
    "backup_phase2",
    "backup_imports",
    "__pycache__",
    "venv",
}


def should_process(path: Path) -> bool:
    if not path.suffix == ".py":
        return False
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return False
    return True


def scan_file(path: Path):
    imports = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [(f"# ERROR parsing {path}: {e}", None)]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append((n.name, path))
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            imports.append((module, path))

    return imports


def main():
    if REPORT.exists():
        REPORT.unlink()

    results = []

    for py in SRC.rglob("*.py"):
        if should_process(py):
            imports = scan_file(py)
            for module, file_path in imports:
                results.append((module, file_path))

    # Write the report
    with open(REPORT, "w") as f:
        for module, file_path in results:
            f.write(f"{module}  <--  {file_path}\n")

    print("\n=== IMPORT SCAN COMPLETE ===")
    print(f"Report written to: {REPORT}")
    print("Open the file to identify which imports must be rewritten.\n")


if __name__ == "__main__":
    main()
