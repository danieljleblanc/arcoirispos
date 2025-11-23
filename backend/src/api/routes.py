# backend/src/api/routes.py

from fastapi import APIRouter

# Authentication / Dev Tools
from .auth_routes import router as auth_router
from .dev_bootstrap_routes import router as dev_bootstrap_router

# POS domain routes
from .customer_routes import router as customers_router
from .sales_routes import router as sales_router
from .tax_rates_routes import router as tax_rates_router
from .payments_routes import router as payments_router
from .sale_lines_routes import router as sale_lines_router
from .terminals_routes import router as terminals_router

# Inventory domain routes
from .items_routes import router as items_router
from .locations_routes import router as locations_router
from .stock_levels_routes import router as stock_levels_router
from .stock_movements_routes import router as stock_movements_router
from .admin_stock_adjust_routes import router as admin_stock_adjust_router


api_router = APIRouter()

# ---------------------------------------------------------
# AUTHENTICATION + DEV TOOLS
# ---------------------------------------------------------
api_router.include_router(auth_router, prefix="/api")
api_router.include_router(dev_bootstrap_router, prefix="/api")

# ---------------------------------------------------------
# POS ROUTES
# ---------------------------------------------------------
api_router.include_router(customers_router,       prefix="/api/pos")
api_router.include_router(sales_router,           prefix="/api/pos")
api_router.include_router(tax_rates_router,       prefix="/api/pos")
api_router.include_router(payments_router,        prefix="/api/pos")
api_router.include_router(sale_lines_router,      prefix="/api/pos")
api_router.include_router(terminals_router,       prefix="/api/pos")

# ---------------------------------------------------------
# INVENTORY ROUTES
# ---------------------------------------------------------
api_router.include_router(items_router,           prefix="/api/inv")
api_router.include_router(locations_router,       prefix="/api/inv")
api_router.include_router(stock_levels_router,    prefix="/api/inv")
api_router.include_router(stock_movements_router, prefix="/api/inv")
api_router.include_router(admin_stock_adjust_router, prefix="/api/inv")
