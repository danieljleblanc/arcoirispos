# backend/src/api/routes.py

from fastapi import APIRouter

from .customer_routes import router as customers_router
from .items_routes import router as items_router
from .sales_routes import router as sales_router
from .locations_routes import router as locations_router
from .stock_levels_routes import router as stock_levels_router
from .stock_movements_routes import router as stock_movements_router
from .tax_rates_routes import router as tax_rates_router
from .payments_routes import router as payments_router
from .sale_lines_routes import router as sale_lines_router
from .terminals_routes import router as terminals_router


api_router = APIRouter()

# POS
api_router.include_router(customers_router, prefix="/pos")
api_router.include_router(sales_router, prefix="/pos")
api_router.include_router(tax_rates_router, prefix="/pos")
api_router.include_router(payments_router, prefix="/pos")
api_router.include_router(sale_lines_router, prefix="/pos")
api_router.include_router(terminals_router, prefix="/pos")


# Inventory
api_router.include_router(items_router, prefix="/inv")
api_router.include_router(locations_router, prefix="/inv")
api_router.include_router(items_router, prefix="/inv")
api_router.include_router(locations_router, prefix="/inv")
api_router.include_router(stock_levels_router, prefix="/inv")
api_router.include_router(stock_movements_router, prefix="/inv")


