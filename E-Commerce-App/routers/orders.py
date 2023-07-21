from fastapi import APIRouter
from models import OrderUpdateDTO
from database import users_collection, orders_collection
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import pydantic
from bson import ObjectId
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str
router = APIRouter(
    prefix="",
    tags=["orders"], )


@router.put("/orders/{orderId}")
async def update_order(orderId: str, order: OrderUpdateDTO):
    order = jsonable_encoder(order)
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        orders_collection.update_one({"_id": ObjectId(orderId)},
                                     {"$set": order})
        return await users_collection.find_one({"_id": ObjectId(orderId)})
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order Id {orderId}.")


@router.get("/orders")
async def get_all_orders():
    fetchedOrders = await orders_collection.find({}).to_list(1000)
    if fetchedOrders is not None:
        return fetchedOrders
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Orders exists .")


@router.get("/orders/{orderId}")
async def get_order_by_id(orderId: str):
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        return fetchedOrder
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order ID {orderId} .")


@router.delete("/orders/{orderId}")
async def delete_order(orderId: str):
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        orders_collection.delete_one({"_id": ObjectId(orderId)})
        return {'detail': f'Order Deleted Successfully with Order ID {orderId}'}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order ID {orderId} .")

