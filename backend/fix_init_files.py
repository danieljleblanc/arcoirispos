from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

print("\n=== CREATING MISSING __init__.py FILES ===\n")

count = 0

for folder in SRC.rglob("*"):
    if folder.is_dir():
        init_file = folder / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# added automatically\n")
            print(f"[ADD] {init_file}")
            count += 1

print(f"\n=== DONE: {count} __init__.py files created ===\n")
