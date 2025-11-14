from pydantic import BaseModel
from src.schemas.sale_schemas import SaleCreate
from src.schemas.payment_schemas import PaymentCreate


class CheckoutRequest(BaseModel):
    sale: SaleCreate
    payment: PaymentCreate
