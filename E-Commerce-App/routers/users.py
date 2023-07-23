import json
from fastapi import APIRouter
from models import UserCreateDTO, UserUpdateDTO, BucketItem, OrderItem, Address, Order
from database import users_collection, orders_collection, products_collection
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import datetime
import pydantic
from typing import List
from bson import ObjectId, json_util
import redis
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str
router = APIRouter(
    prefix="",
    tags=["users"], )


@router.get("/users/{userId}", status_code=status.HTTP_200_OK)
async def get_user_by_id(userId: str):
    cacheduser = r.hget(f'users', f'{userId}')
    if cacheduser is not None:
        return json_util.loads(cacheduser)
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"},
                                                  {"bucket": 0, "orders": 0, "status": 0, "created_at": 0,
                                                   "user_type": 0})
    if fetchedUser is not None:
        r.hset(f'users', f'{userId}', json_util.dumps(fetchedUser))
        r.expire('users',300)
        return fetchedUser
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.get("/users", status_code= status.HTTP_200_OK)
async def get_all_users():
    cachedusers = r.hgetall('users')
    if len(cachedusers) !=0:
        userlist = list()
        for key in cachedusers.keys():
            userlist.append(json_util.loads(cachedusers.get(key)))
        return userlist
    users = await users_collection.find({"status": "Active"}, {"bucket": 0, "orders": 0, "status": 0, "created_at": 0,
                                                               "user_type": 0}).to_list(1000)
    if users is None:
        raise HTTPException(status.HTTP_204_NO_CONTENT, 'No Users Available.')
    else:
        for user in users:
            r.hset('users', f'{str(user["_id"])}', json_util.dumps(user))
        r.expire('users', 300)
        return users


@router.put("/users/{userId}", status_code=status.HTTP_200_OK)
async def update_user_by_id(userId: str, user: UserUpdateDTO):
    user = jsonable_encoder(user)
    isUserValid = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if isUserValid:
        updated_user = await users_collection.update_one({"_id": ObjectId(userId)},
                                                         {"$set": user})
        if updated_user is not None and updated_user.acknowledged:
            updated_user = await users_collection.find_one({"_id": ObjectId(userId)},
                                                           {"bucket": 0, "orders": 0, "status": 0, "created_at": 0,
                                                            "user_type": 0})
            r.hset('users', f'{userId}', json_util.dumps(updated_user))
            r.expire('users', 300)
            return updated_user
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.delete("/users/{userId}", status_code=status.HTTP_200_OK)
async def delete_user_by_id(userId: str):
    isUserValid = await users_collection.find_one({"_id": ObjectId(userId)}, {"status": "Active"})
    if isUserValid:
        deleted_user = await users_collection.update_one({"_id": ObjectId(userId)}, {"$set": {"status": "Deactivate"}})
        if deleted_user is not None and deleted_user.acknowledged:
            return {"detail": f"User deleted successfully with User id {userId}."}
            r.hdel('users',f'{userId}')
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateDTO):
    user = jsonable_encoder(user)
    is_email_used = await users_collection.find_one({"email": user["email"]})
    if not is_email_used:
        user["bucket"] = []
        user["orders"] = []
        user["user_type"] = "User"
        user["created_at"] = datetime.datetime.utcnow()
        user["status"] = "Active"
        new_user = await users_collection.insert_one(user)
        created_user = await users_collection.find_one({"_id": new_user.inserted_id},
                                                       {"bucket": 0, "orders": 0, "status": 0, "created_at": 0,
                                                        "user_type": 0})
        r.hset('users', str(created_user["_id"]), json_util.dumps(created_user))
        r.expire('users', 300)
        return created_user
    else:
        return {'detail': 'Email Already In Use. Please use Different Email.'}


@router.post("/users/{userId}/addItemToBucket", status_code=status.HTTP_201_CREATED)
async def add_item_to_bucket(userId: str, item: BucketItem):
    item = jsonable_encoder(item)
    quantity = item["quantity"]
    product_id = item["product_id"]
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        fetchedProduct = await products_collection.find_one({"_id": ObjectId(item["product_id"]), "status": "Active"})
        if fetchedProduct is not None:
            if fetchedProduct["quantity"] >= item["quantity"]:
                for bucketItem in fetchedUser["bucket"]:
                    if bucketItem["product_id"] == product_id:
                        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Product Already Exists In Bucket {product_id}")
                users_collection.update_one({"_id": ObjectId(userId)}, {"$push": {"bucket": item}})
                bucket =  await users_collection.find_one({"_id": ObjectId(userId)}, {"_id": 0, "bucket": 1})
                r.set(f'user:{userId}:bucket', json_util.dumps(bucket))
                r.expire(f'user:{userId}:bucket',300)
                return bucket
            else:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    f"Requested quantities {quantity} of product {product_id} are not available. Max "
                                    f"Available Quantity is {fetchedProduct.quantity}.")
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Product exists with Product Id {product_id}.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.put("/users/{userId}/updateItemToBucket", status_code=status.HTTP_200_OK)
async def update_item_to_bucket(userId: str, item: BucketItem):
    item = jsonable_encoder(item)
    quantity = item["quantity"]
    product_id = item["product_id"]
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        fetchedProduct = await products_collection.find_one({"_id": ObjectId(item["product_id"]), "status": "Active"})
        if fetchedProduct is not None:
            if fetchedProduct["quantity"] >= item["quantity"]:
                for bucketItem in fetchedUser["bucket"]:
                    if bucketItem.product_id == product_id:
                        users_collection.update_one({"_id": ObjectId(userId), "bucket.product_id": product_id},
                                                    {"$set": {"bucket.$.quantity": quantity}})
                        bucket = await users_collection.find_one({"_id": ObjectId(userId)}, {"_id": 0, "bucket": 1})
                        r.set(f'user:{userId}:bucket', json_util.dumps(bucket))
                        r.expire(f'user:{userId}:bucket', 300)
                    else:
                        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Product Doesn't Exists In Bucket {product_id}")
            else:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    f"Requested quantities {quantity} of product {product_id} are not available. Max "
                                    f"Available Quantity is {fetchedProduct.get('quantity')}.")
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Product exists with Product Id {product_id}.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.delete("/users/{userId}/deleteItemFromBucket", status_code=status.HTTP_200_OK)
async def delete_item_to_bucket(userId: str, productId: str):
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        for bucketItem in fetchedUser["bucket"]:
            if bucketItem.product_id == productId:
                users_collection.update_one({"_id": ObjectId(userId)},
                                            {"$pull": {"bucket": {"product_id": productId}}})
                bucket = await users_collection.find_one({"_id": ObjectId(userId)}, {"_id": 0, "bucket": 1})
                r.set(f'user:{userId}:bucket', json_util.dumps(bucket))
                return {'message':'item deleted successfully from bucket'}
            else:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Product Doesn't Exists In Bucket {productId}")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.delete("/users/{userId}/deleteBucket", status_code=status.HTTP_200_OK)
async def delete_bucket(userId: str):
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        if len(fetchedUser["bucket"]) != 0:
            for bucketItem in fetchedUser["bucket"]:
                users_collection.update_one({"_id": ObjectId(userId)},
                                            {"$pull": {"bucket": {"product_id": bucketItem["product_id"]}}})
            r.delete(f'user:{userId}:bucket')
            return {'detail': f'Bucket Deleted Successfully For User {userId}.'}
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Items In Bucket To Delete.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.get("/"
            "users/{userId}/getBucket", status_code=status.HTTP_200_OK)
async def get_bucket(userId: str):
    userBucket = r.get(f'user:{userId}:bucket')
    if userBucket is not None:
        return json_util.loads(userBucket)
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        if len(fetchedUser["bucket"]) != 0:
            bucket = await users_collection.aggregate([
                {
                    "$unwind": {
                        "path": "$bucket",
                        "preserveNullAndEmptyArrays": False,
                    },
                },
                {
                    "$addFields": {
                        "product_idstr": {
                            "$toObjectId": "$bucket.product_id",
                        },
                        "ordered_quantity": "$bucket.quantity"
                    },
                },
                {
                    "$lookup": {
                        "from": "products",
                        "localField": "product_idstr",
                        "foreignField": "_id",
                        "as": "bucket_product",
                    },
                },
                {
                    "$project": {
                        "bucket_product": 1, "ordered_quantity": 1
                    },
                },
                {
                    "$unwind": {
                        "path": "$bucket_product",
                        "preserveNullAndEmptyArrays": False
                    }
                }, {
                    "$addFields": {
                        "ProductTotalPrice": {"$multiply": ["$bucket_product.price", "$ordered_quantity"]},
                        "ProductDiscount": {"$multiply": ["$bucket_product.discount", "$ordered_quantity"]}
                    }
                }, {
                    "$addFields": {
                        "ProductPriceToPay": {"$subtract": ["$ProductTotalPrice", "$ProductDiscount"]}
                    }
                },
                {
                    "$project": {
                        "bucket_product.status": 0,
                        "bucket_product.created_at": 0,
                        "bucket_product.quantity": 0,
                        "bucket_product.reviews": 0,
                        "bucket_product.rating": 0
                    }
                },
                {
                    "$group": {
                        "_id": "$_id",
                        "bucketProducts": {"$push": "$$ROOT"},
                        "BucketTotal": {
                            "$sum": "$ProductTotalPrice"
                        },
                        "BucketDiscount": {"$sum": "$ProductDiscount"},
                    }
                },
                {
                    "$addFields": {
                        "BucketPriceToPay": {"$subtract": ["$BucketTotal", "$BucketDiscount"]}}
                }, {"$project": {
                    "_id": 0, "bucketProduct.quantity": 0, "bucketProducts._id": 0
                }}
            ]).to_list(1000)
            r.set(f'user:{userId}:bucket', json_util.dumps(bucket))
            r.expire(f'user:{userId}:bucket', 300)
            return bucket
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Items In Bucket.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.post("/users/{userId}/createOrder", status_code=status.HTTP_201_CREATED)
async def create_order(userId: str, address: Address, modeOfPayment: str, transactionId: str):
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        if len(fetchedUser["bucket"]) != 0:
            user_bucket = await get_bucket(userId)
            order_items = list()
            for bucketItem in user_bucket[0]["bucketProducts"]:
                product = bucketItem["bucket_product"]
                fetchedproduct = await products_collection.find_one(
                    {"_id": ObjectId(product["_id"]), "status": "Active"})
                if fetchedproduct is not None:
                    if bucketItem["ordered_quantity"] <= fetchedproduct["quantity"]:
                        order_items.append(
                            OrderItem(product_id=str(product["_id"]), quantity=bucketItem["ordered_quantity"],
                                      price=product["price"], discount=product["discount"],
                                      TotalPrice=bucketItem["ProductTotalPrice"],
                                      TotalDiscount=bucketItem["ProductDiscount"],
                                      priceToPay=bucketItem["ProductPriceToPay"]))
                    else:
                        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Product {product['_id']} is out of stock "
                                                                       f"currently.")
                else:
                    raise HTTPException(status.HTTP_404_NOT_FOUND,
                                        f"Product {product['_id']} is not available to order.")
            order = Order(user_id=userId, items=order_items, total_price=user_bucket[0]["BucketTotal"],
                          total_discount=user_bucket[0]["BucketDiscount"],
                          price_to_pay=user_bucket[0]["BucketPriceToPay"],
                          delivery_address=address, received_by=None, status="Placed", mode_of_payment=modeOfPayment,
                          ordered_date=datetime.datetime.utcnow(), delivery_date=None, transactionID=transactionId)
            order = jsonable_encoder(order)
            new_order = await orders_collection.insert_one(order)
            created_order = await orders_collection.find_one({"_id": new_order.inserted_id})
            r.hset(f'user:{userId}:orders', str(created_order["_id"]), json_util.dumps(created_order))
            r.expire(f'user:{userId}:orders',300)
            return created_order
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Items In Bucket.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@router.get("/userId/{userId}/getAllOrders", status_code=status.HTTP_200_OK)
async def get_all_orders_for_user(userId: str):
    userorders = r.hgetall(f'user:{userId}:orders')
    if len(userorders) !=0:
        orderlist = list()
        for key in userorders.keys():
            orderlist.append(json_util.loads(userorders.get(key)))
        return orderlist
    fetchedUser = users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        fetchedOrders = await orders_collection.find({"user_id": userId}).to_list(1000)
        if fetchedOrders is not None:
            for order in fetchedOrders:
                r.hset(f'user:{userId}:orders', str(order["_id"]), json_util.dumps(order))
            return fetchedOrders
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Orders exists for User ID {userId} .")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User ID {userId} .")
