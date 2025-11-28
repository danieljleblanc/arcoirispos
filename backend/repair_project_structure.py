#!/usr/bin/env python3
"""
Automated Repair Script for arcoirispos/backend
------------------------------------------------

This script fixes all import-path corruption caused by old folder structures,
including:
    - "app.<domain>.app.<module>"
    - "app.inventory.app.*"
    - "app.pos.app.*"
    - "app.org.app.*"
    - "app.accounting.app.*"
    - ForeignKey("app.pos.app....")
    - broken 'from app import <Model>' imports

It rewrites everything to the correct structure:
    src.app.<domain>.models.<model>_models
    src.app.<domain>.services.<service>
    src.app.<domain>.routes.<route>

It also creates backups: filename.py.bak
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "app"

# Patterns to eliminate entirely
REMOVE_PATTERNS = [
    r"\.app\.",          # app.pos.app.routes → pos.routes
    r"app\.",            # leading "app." if wrong
]

# Map incorrect → correct namespaces for imports
REWRITE_MAP = {
    # Accounting
    r"src\.app\.accounting\.app\.chart_of_accounts\.models": "src.app.accounting.models.account_models",
    r"app\.accounting\.app\.chart_of_accounts\.models": "src.app.accounting.models.account_models",

    # Inventory
    r"src\.app\.inventory\.app\.items\.models": "src.app.inventory.models.item_models",
    r"src\.app\.inventory\.app\.locations\.models": "src.app.inventory.models.location_models",
    r"src\.app\.inventory\.app\.stock_levels\.models": "src.app.inventory.models.stock_level_models",
    r"src\.app\.inventory\.app\.stock_movements\.models": "src.app.inventory.models.stock_movement_models",

    # POS
    r"src\.app\.pos\.app\.sales\.models": "src.app.pos.models.sale_models",
    r"src\.app\.pos\.app\.sale_lines\.models": "src.app.pos.models.sale_models",
    r"src\.app\.pos\.app\.terminals\.models": "src.app.pos.models.terminal_models",
    r"src\.app\.pos\.app\.customers\.models": "src.app.pos.models.customer_models",
    r"src\.app\.pos\.app\.payments\.models": "src.app.pos.models.payment_models",
    r"src\.app\.pos\.app\.tax_rates\.models": "src.app.pos.models.tax_rate_models",

    # Org
    r"src\.app\.org\.app\.user_models\.models": "src.app.org.models.user_models",
}

# Patterns for ForeignKey() cleanup
FOREIGNKEY_FIX = [
    (r'"app\.pos\.app\.sales\.models\.sale_id"', '"pos.sales.sale_id"'),
    (r'"app\.pos\.app\.sale_lines\.models\.sale_line_id"', '"pos.sale_lines.sale_line_id"'),
    (r'"app\.pos\.app\.customers\.models\.customer_id"', '"pos.customers.customer_id"'),
    (r'"app\.pos\.app\.tax_rates\.models\.tax_id"', '"pos.tax_rates.tax_id"'),
    (r'"app\.pos\.app\.terminals\.models\.terminal_id"', '"pos.terminals.terminal_id"'),
    (r'"app\.inventory\.app\.items\.models\.item_id"', '"inv.items.item_id"'),
    (r'"app\.inventory\.app\.locations\.models\.location_id"', '"inv.locations.location_id"'),
]

# Fix "from app import Model" mistakes
APP_IMPORT_FIX = {
    r"from app import (\w+)": r"from src.app import \1",
}


def rewrite_text(content: str) -> str:
    """Apply all transformations to file content."""

    # Remove leftover ".app." segments
    for pat in REMOVE_PATTERNS:
        content = re.sub(pat, ".", content)

    # Rewrite incorrect namespaces
    for wrong, correct in REWRITE_MAP.items():
        content = re.sub(wrong, correct, content)

    # ForeignKey corrections
    for wrong, correct in FOREIGNKEY_FIX:
        content = re.sub(wrong, correct, content)

    # Fix "from app import X"
    for wrong, correct in APP_IMPORT_FIX.items():
        content = re.sub(wrong, correct, content)

    return content


def process_file(path: Path):
    """Rewrite content of a Python file."""
    text = path.read_text()
    new_text = rewrite_text(text)

    if new_text != text:
        backup = path.with_suffix(path.suffix + ".bak")
        path.rename(backup)
        path.write_text(new_text)
        print(f"✔ Fixed: {path}")


def main():
    print("\n=== AUTOMATIC PROJECT STRUCTURE REPAIR ===\n")

    py_files = list(SRC.rglob("*.py"))

    for file in py_files:
        process_file(file)

    print("\n=== COMPLETE ===")
    print("Backups saved as *.py.bak\n")


if __name__ == "__main__":
    main()
