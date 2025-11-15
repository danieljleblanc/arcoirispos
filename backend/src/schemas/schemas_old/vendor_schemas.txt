from pydantic import BaseModel

class VendorCreate(BaseModel):
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None

class VendorOut(BaseModel):
    id: int
    name: str
    contact_name: str | None
    email: str | None
    phone: str | None

    class Config:
        from_attributes = True
