from pydantic import BaseModel
from hw_2.entities.Item_cart import ItemCart

class Cart(BaseModel):
    id: int
    items: list[ItemCart]
    price: float