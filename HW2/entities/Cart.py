from pydantic import BaseModel
from HW2.entities.Item_cart import ItemCart

class Cart(BaseModel):
    id: int
    items: list[ItemCart]
    price: float