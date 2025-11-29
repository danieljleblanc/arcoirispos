# backend/src/app/api_router.py

from fastapi import APIRouter

# ---------------------------------------------------------
# AUTH
# ---------------------------------------------------------
from src.app.auth.routes.auth_routes import router as auth_routes

# ---------------------------------------------------------
# INVENTORY ROUTES
# ---------------------------------------------------------
from src.app.inventory.routes.items_routes import router as items_routes
from src.app.inventory.routes.locations_routes import router as locations_routes
from src.app.inventory.routes.stock_levels_routes import router as stock_levels_routes
from src.app.inventory.routes.stock_movements_routes import router as stock_movements_routes
from src.app.inventory.routes.admin_stock_adjust_routes import router as admin_stock_adjust_routes

# ---------------------------------------------------------
# ORGANIZATION ROUTES 
# ---------------------------------------------------------
from src.app.org.routes.organization_settings_routes import router as org_settings_router

# ---------------------------------------------------------
# POS ROUTES
# ---------------------------------------------------------
from src.app.pos.routes.customer_routes import router as customer_routes
from src.app.pos.routes.payments_routes import router as payments_routes
from src.app.pos.routes.sale_lines_routes import router as sale_lines_routes
from src.app.pos.routes.sales_routes import router as sales_routes
from src.app.pos.routes.tax_rates_routes import router as tax_rates_routes
from src.app.pos.routes.terminals_routes import router as terminals_routes


# ---------------------------------------------------------
# ROOT ROUTER
# ---------------------------------------------------------
api_router = APIRouter()

# ---------------------------------------------------------
# REGISTER ROUTES
# ---------------------------------------------------------
api_router.include_router(auth_routes)

api_router.include_router(items_routes)
api_router.include_router(locations_routes)
api_router.include_router(stock_levels_routes)
api_router.include_router(stock_movements_routes)
api_router.include_router(admin_stock_adjust_routes)
api_router.include_router(org_settings_router)
api_router.include_router(customer_routes)
api_router.include_router(payments_routes)
api_router.include_router(sale_lines_routes)
api_router.include_router(sales_routes)
api_router.include_router(tax_rates_routes)
api_router.include_router(terminals_routes)
