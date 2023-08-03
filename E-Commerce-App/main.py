from fastapi import FastAPI
from .routers import users, products, orders
import redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)
app = FastAPI()
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/")
async def root():
    return {"message": "Welcome To E Commerce App!"}
