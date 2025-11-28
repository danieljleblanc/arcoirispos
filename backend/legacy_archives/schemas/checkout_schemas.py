from pydantic import BaseModel
from app.sale_schemas import SaleCreate
from app.payment_schemas import PaymentCreate


class CheckoutRequest(BaseModel):
    sale: SaleCreate
    payment: PaymentCreate
