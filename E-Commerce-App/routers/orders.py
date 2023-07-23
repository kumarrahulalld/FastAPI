import json

from fastapi import APIRouter
from models import OrderUpdateDTO
from database import users_collection, orders_collection
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import pydantic
from bson import ObjectId, json_util
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str
import redis
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
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
        created_order =  await users_collection.find_one({"_id": ObjectId(orderId)})
        r.hset('orders', f'{orderId}', json_util.dumps(created_order))
        r.expire('orders', 300)
        return created_order
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order Id {orderId}.")


@router.get("/orders")
async def get_all_orders():
    cachedorders = r.hgetall('orders')
    if len(cachedorders) !=0:
        orderlist = list()
        for key in cachedorders.keys():
            orderlist.append(json_util.loads(cachedorders.get(key)))
        return orderlist
    fetchedOrders = await orders_collection.find({}).to_list(1000)
    if fetchedOrders is not None:
        for order in fetchedOrders:
            r.hset('orders', f'{str(order["_id"])}', json_util.dumps(order))
        r.expire('orders', 300)
        return fetchedOrders
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Orders exists .")


@router.get("/orders/{orderId}")
async def get_order_by_id(orderId: str):
    cachedorder = r.hget('orders', f'{orderId}')
    if cachedorder is not None:
        return json.loads(cachedorder)
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        r.hset('orders', f'{orderId}', json_util.dumps(fetchedOrder))
        r.expire('orders', 300)
        return fetchedOrder
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order ID {orderId} .")


@router.delete("/orders/{orderId}")
async def delete_order(orderId: str):
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        orders_collection.delete_one({"_id": ObjectId(orderId)})
        r.hdel('orders', f'{orderId}')
        return {'detail': f'Order Deleted Successfully with Order ID {orderId}'}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order ID {orderId} .")

