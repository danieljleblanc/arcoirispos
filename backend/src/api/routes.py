from fastapi import APIRouter
from src.api.sales_routes import router as sales_router
from src.api.item_routes import router as item_router
from src.api.customer_routes import router as customer_router
from src.api.inventory_vendor_routes import router as vendor_router
from src.api.inventory_stock_routes import router as stock_router
from src.api.inventory_transaction_routes import router as transaction_router



router = APIRouter()

router.include_router(sales_router)
router.include_router(item_router)
router.include_router(customer_router)
router.include_router(vendor_router)
router.include_router(stock_router)
router.include_router(transaction_router)
