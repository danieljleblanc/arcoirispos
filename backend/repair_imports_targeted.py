#!/usr/bin/env python3

import os
import re
import shutil

BASE = "src/app"

# -------------------------------------------------------------------
# Utility: replace text in a file with backup
# -------------------------------------------------------------------
def replace_in_file(filepath, replacements):
    if not os.path.exists(filepath):
        print(f"[SKIP] File not found: {filepath}")
        return

    with open(filepath, "r") as f:
        original = f.read()

    new_text = original
    for pattern, repl in replacements.items():
        new_text = re.sub(pattern, repl, new_text)

    if new_text != original:
        backup = filepath + ".bak"
        shutil.copyfile(filepath, backup)
        with open(filepath, "w") as f:
            f.write(new_text)
        print(f"[FIXED] {filepath} (backup saved as .bak)")
    else:
        print(f"[OK] {filepath} (no changes needed)")


# -------------------------------------------------------------------
# 1. FIX api_router POS import paths
# -------------------------------------------------------------------
api_router = f"{BASE}/api_router.py"

api_router_replacements = {
    r"from src\.app\.pos\.routes\.customers_routes": 
        "from src.app.pos.routes.customer_routes",

    r"from src\.app\.pos\.routes\.payment_routes":
        "from src.app.pos.routes.payments_routes",

    r"from src\.app\.pos\.routes\.payments_routes":
        "from src.app.pos.routes.payments_routes",

    r"from src\.app\.pos\.routes\.sale_line_routes":
        "from src.app.pos.routes.sale_lines_routes",

    r"from src\.app\.pos\.routes\.sale_lines_routes":
        "from src.app.pos.routes.sale_lines_routes",

    r"from src\.app\.pos\.routes\.sales_route":
        "from src.app.pos.routes.sales_routes",

    r"from src\.app\.pos\.routes\.sales_routes":
        "from src.app.pos.routes.sales_routes",

    r"from src\.app\.pos\.routes\.tax_rate_routes":
        "from src.app.pos.routes.tax_rates_routes",

    r"from src\.app\.pos\.routes\.terminals_route":
        "from src.app.pos.routes.terminals_routes",

    r"from src\.app\.pos\.routes\.terminals_routes":
        "from src.app.pos.routes.terminals_routes",
}

# -------------------------------------------------------------------
# 2. FIX POS service model imports
# -------------------------------------------------------------------

POS_SERVICE_FILES = {
    "customer_service.py": {
        r"from src\.app import Customer":
            "from src.app.pos.models.customer_models import Customer"
    },
    "payment_service.py": {
        r"from src\.app import Payment":
            "from src.app.pos.models.payment_models import Payment"
    },
    "sale_line_service.py": {
        r"from src\.app import SaleLine":
            "from src.app.pos.models.sale_models import SaleLine"
    },
    "sales_service.py": {
        r"from src\.app import Sale":
            "from src.app.pos.models.sale_models import Sale"
    },
    "tax_rate_service.py": {
        r"from src\.app import TaxRate":
            "from src.app.pos.models.tax_rate_models import TaxRate"
    },
    "terminal_service.py": {
        r"from src\.app import Terminal":
            "from src.app.pos.models.terminal_models import Terminal"
    }
}

# -------------------------------------------------------------------
# 3. FIX Alembic env.py entrypoint
# -------------------------------------------------------------------

alembic_env = f"{BASE}/infrastructure/migrations/env.py"

alembic_replacements = {
    # Replace direct context.is_offline_mode()
    r"(?s)if context\.is_offline_mode\(\):.*?run_migrations_online\(\)":
    """def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()

run()""",
}

# -------------------------------------------------------------------
# APPLY FIXES
# -------------------------------------------------------------------

print("\n=== APPLYING TARGETED IMPORT REPAIRS ===\n")

# 1
replace_in_file(api_router, api_router_replacements)

# 2
for filename, fixes in POS_SERVICE_FILES.items():
    path = f"{BASE}/pos/services/{filename}"
    replace_in_file(path, fixes)

# 3
replace_in_file(alembic_env, alembic_replacements)

print("\n=== DONE ===")
print("Run the validator again:")
print("   ./venv/bin/python validate_project.py\n")
