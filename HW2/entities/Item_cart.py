from pydantic import BaseModel

class ItemCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool