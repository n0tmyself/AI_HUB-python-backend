from fastapi import APIRouter, HTTPException, Response
from http import HTTPStatus
from pydantic import NonNegativeFloat, NonNegativeInt, PositiveInt
from hw_2.entities.Cart import Cart
from hw_2.entities.Item_cart import ItemCart
from hw_2.entities.Item import Item 

router_cart = APIRouter(prefix="/cart")
router_item = APIRouter(prefix="/item")

carts = {}

items = {1: Item(id = 1, name = "test0", price=100), 2: Item(id = 2, name = "test1", price = 300, status_delete= True)}

def generate_id_cart():
    return max(carts.keys(), default=0) + 1

def generate_id_item():
    return max(items.keys(), default=0) + 1

@router_cart.post("")
async def create_cart(response: Response):
    id_cart = generate_id_cart()
    carts[id_cart] = Cart(id=id_cart, items=[], price=0)
    response.headers["location"] = f"/carts/{id_cart}"
    response.status_code = HTTPStatus.CREATED
    
    return {"id": id_cart}

@router_cart.get("/{id}", status_code=HTTPStatus.OK)
async def get_cart(id: int):
    if id not in carts.keys():
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return carts[id]

@router_cart.get("", status_code=HTTPStatus.OK)
async def get_cart_params(offset: NonNegativeInt = 0, limit: PositiveInt = 10, 
                          min_price: NonNegativeFloat = None, max_price: NonNegativeFloat = None, 
                          min_quantity: NonNegativeInt = None, max_quantity: NonNegativeInt = None):
    
    fil_carts = list(carts.values())
    
    if min_price is not None:
        fil_carts = [cart for cart in fil_carts if cart.price >= min_price]
    if max_price is not None:
        fil_carts = [cart for cart in fil_carts if cart.price <= max_price]
    if min_quantity is not None:
        fil_carts = [cart for cart in fil_carts if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity is not None:
        fil_carts = [cart for cart in fil_carts if sum(item.quantity for item in cart.items) <= max_quantity]
    
    fil_carts = fil_carts[offset: offset + limit]
    response = [{"id": cart.id, "quantity": sum(item.quantity for item in cart.items), "price": cart.price} for cart in fil_carts]
    
    return response

@router_cart.post("/{cart_id}/add/{item_id}", status_code=HTTPStatus.OK)
async def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts.keys():
        raise HTTPException(status_code=404, detail="Cart not found")
    if item_id not in items.keys():
        raise HTTPException(status_code=404, detail="Item not found")
    
    cart = carts[cart_id]
    item = items[item_id]
    
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            
            return {"message": "Quantity increased"}
    
    cart.items.append(ItemCart(id=item.id, name=item.name, quantity=1, available=not item.status_delete))
    cart.price += item.price
    
    return {"message": "Item added to cart"}

@router_item.post("", status_code=HTTPStatus.CREATED)
async def add_new_item(item: dict):
    id_item = generate_id_item()
    item = Item(id=id_item, name=item["name"], price=item["price"])
    items[id_item] = item
    
    return item

@router_item.get("/{id}", status_code=HTTPStatus.OK)
async def get_item(id: int):
    if id not in items.keys():
        raise HTTPException(status_code=404, detail ="Item doesnt exist")
    if items[id].status_delete == True:
        raise HTTPException(status_code=404, detail="Item has been deleted")
    return items[id]

@router_item.get("", status_code=HTTPStatus.OK)
async def get_item_param(offset: NonNegativeInt = 0, limit: PositiveInt = 10, 
                         min_price: NonNegativeFloat = None, max_price: NonNegativeFloat = None,
                         show_deleted: bool = False):
    fil_items = list(items.values())
    
    if not show_deleted:
        fil_items = [item for item in fil_items if not item.status_delete]
    if min_price is not None:
        fil_items = [item for item in fil_items if item.price >= min_price]
    if max_price is not None:
        fil_items = [item for item in fil_items if item.price <= max_price]
    
    fil_items = fil_items[offset: offset + limit]
    return fil_items

@router_item.put("/{id}", status_code=HTTPStatus.OK)
async def put_item(id: int, item: dict):
    if ("name" or "price") not in item.keys():
        raise HTTPException(status_code=422, detail="Not required parameters")
    updated_item = Item(id=id, name=item["name"], price=item["price"])
    items[id] = updated_item
    
    return updated_item

@router_item.patch("/{id}", status_code=HTTPStatus.OK)
async def patch_item(id: int, item: dict):
    old_item = items[id]
    if old_item.status_delete == True:
        raise HTTPException(status_code=304, detail="Item not modified")

    invalid_keys = set(item.keys()) - set(old_item.model_dump().keys())
    if invalid_keys:
        raise HTTPException(status_code=422, detail="Wrong field")

    name = item.get("name", old_item.name)
    price = item.get("price", old_item.price)
    status_delete = item.get("status_delete", old_item.status_delete)
    
    updated_item = Item(id=id, name=name, price=price, status_delete=status_delete)
    
    if old_item.status_delete != updated_item.status_delete:
        raise HTTPException(status_code=422, detail="status delete cannot be changed")
    
    items[id] = updated_item
    
    return updated_item

@router_item.delete("/{id}", status_code=HTTPStatus.OK)
async def delete_item(id:int):
    if id not in items.keys():
        raise HTTPException(status_code=404, detail="Item not found")
    items[id].status_delete = True
    
    return items[id]