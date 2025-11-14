from pydantic import BaseModel


class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None


class CustomerOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str | None
    phone: str | None

    class Config:
        from_attributes = True
