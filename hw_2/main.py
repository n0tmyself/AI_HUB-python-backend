from fastapi import FastAPI
from hw_2.routers.quaries import router_cart, router_item

app = FastAPI(title="Shop API")

app.include_router(router_cart)
app.include_router(router_item)