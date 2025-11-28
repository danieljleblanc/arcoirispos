import re
import sys
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
APP = SRC / "app"

BACKUP_DIR = ROOT / "backup_phase5_imports"
BACKUP_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------------
# MODEL MAP — all objects that should not be imported from app.__init__
# -------------------------------------------------------------------
MODEL_LOCATIONS = {
    "Base": "src.app.core.base",
    "ChartOfAccount": "src.app.accounting.models.account_models",
    "CustomerBalance": "src.app.accounting.models.customer_balance_models",
    "Journal": "src.app.accounting.models.journal_models",
    "JournalLine": "src.app.accounting.models.journal_line_models",
    "BankAccount": "src.app.accounting.models.bank_account_models",

    "Item": "src.app.inventory.models.item_models",
    "StockLevel": "src.app.inventory.models.stock_level_models",
    "StockMovement": "src.app.inventory.models.stock_movement_models",
    "Location": "src.app.inventory.models.location_models",

    "Terminal": "src.app.pos.models.terminal_models",
    "Sale": "src.app.pos.models.sale_models",
    "SaleLine": "src.app.pos.models.sale_models",
    "Customer": "src.app.pos.models.customer_models",
    "Payment": "src.app.pos.models.payment_models",
    "TaxRate": "src.app.pos.models.tax_rate_models",

    "User": "src.app.org.models.user_models",
    "Role": "src.app.org.models.role_models",
    "Organization": "src.app.org.models.organization_models",
}

# universal rewrite patterns
REWRITE_RULES = [
    # fix bad nested paths
    (r"from\s+app\.app\.", "from src.app."),
    (r"import\s+app\.app\.", "import src.app."),

    # fix base imports
    (r"from\s+app\.core\.base\b", "from src.app.core.base"),

    # fix direct app imports
    (r"from\s+app\.", "from src.app."),
    (r"import\s+app\.", "import src.app."),
]

MODEL_REGEX = re.compile(r"from\s+app\s+import\s+([A-Za-z_][A-Za-z0-9_,\s]+)")


def fix_file(path: Path):
    rel = str(path.relative_to(ROOT))
    backup_path = BACKUP_DIR / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(path, backup_path)

    text = path.read_text()

    # Apply simple rewrite rules
    for pattern, replacement in REWRITE_RULES:
        text = re.sub(pattern, replacement, text)

    # Fix "from app import X, Y"
    matches = MODEL_REGEX.findall(text)
    for match in matches:
        objs = [obj.strip() for obj in match.split(",")]
        for obj in objs:
            if obj in MODEL_LOCATIONS:
                correct_path = MODEL_LOCATIONS[obj]
                text = re.sub(
                    rf"from\s+app\s+import\s+{obj}\b",
                    f"from {correct_path} import {obj}",
                    text
                )

    path.write_text(text)
    return True


def main():
    print("\n=== PHASE 5: GLOBAL IMPORT REWRITE STARTING ===\n")

    py_files = [p for p in SRC.rglob("*.py") if "__pycache__" not in p.parts]

    for p in py_files:
        try:
            fix_file(p)
            print(f"[FIXED] {p}")
        except Exception as e:
            print(f"[ERROR] {p} — {e}")

    print("\n=== PHASE 5 COMPLETE ===")
    print(f"Backups at: {BACKUP_DIR}\n")
    print("➡ Run validate_project.py again.")


if __name__ == "__main__":
    main()
