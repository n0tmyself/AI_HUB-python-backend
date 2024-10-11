from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float
    status_delete: bool = False