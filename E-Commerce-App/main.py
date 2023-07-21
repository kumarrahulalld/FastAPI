import datetime
from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
import pydantic
from typing import List
from bson import ObjectId
from database import users_collection, products_collection, orders_collection
from models import UserCreateDTO, UserUpdateDTO, ProductUpdateDTO, ProductCreateDTO, BucketItem, Order, OrderItem, \
    Address, OrderUpdateDTO

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

app = FastAPI()


@app.get("/users/{userId}", response_model=UserCreateDTO, status_code=status.HTTP_200_OK)
async def get_user_by_id(userId: str):
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"},
                                                  {"bucket": 0, "orders": 0, "status": 0, "created_at": 0,
                                                   "user_type": 0})
    if fetchedUser is not None:
        return fetchedUser
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.get("/users", response_model=List[UserCreateDTO], status_code=status.HTTP_200_OK)
async def get_all_users():
    users = await users_collection.find({"status": "Active"}, {"bucket": 0, "orders": 0, "status": 0, "created_at": 0,
                                                               "user_type": 0}).to_list(1000)
    if users is None:
        raise HTTPException(status.HTTP_204_NO_CONTENT, 'No Users Available.')
    else:
        return users


@app.put("/users/{userId}", response_model=UserCreateDTO, status_code=status.HTTP_200_OK)
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
            return updated_user
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.delete("/users/{userId}", status_code=status.HTTP_200_OK)
async def delete_user_by_id(userId: str):
    isUserValid = await users_collection.find_one({"_id": ObjectId(userId)}, {"status": "Active"})
    if isUserValid:
        deleted_user = await users_collection.update_one({"_id": ObjectId(userId)}, {"$set": {"status": "Deactivate"}})
        if deleted_user is not None and deleted_user.acknowledged:
            return {"detail": f"User deleted successfully with User id {userId}."}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.post("/users", status_code=status.HTTP_201_CREATED)
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
        return created_user
    else:
        return {'detail': 'Email Already In Use. Please use Different Email.'}


@app.get("/products/{productId}", response_model=ProductCreateDTO, status_code=status.HTTP_200_OK)
async def get_product_by_id(productId: str):
    fetchedproduct = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"},
                                                        {"status": 0, "created_at": 0})
    if fetchedproduct is not None:
        return fetchedproduct
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@app.get("/products", response_model=List[ProductCreateDTO], status_code=status.HTTP_200_OK)
async def get_all_products():
    products = await products_collection.find({"status": "Active"}, {"status": 0, "created_at": 0}).to_list(1000)
    if products is None:
        raise HTTPException(status.HTTP_204_NO_CONTENT, 'No products Available.')
    else:
        return products


@app.put("/products/{productId}", response_model=ProductUpdateDTO, status_code=status.HTTP_200_OK)
async def update_product_by_id(productId: str, product: ProductUpdateDTO):
    product = jsonable_encoder(product)
    isproductValid = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"})
    if isproductValid:
        updated_product = await products_collection.update_one({"_id": ObjectId(productId)},
                                                               {"$set": product})
        if updated_product is not None and updated_product.acknowledged:
            updated_product = await products_collection.find_one({"_id": ObjectId(productId)},
                                                                 {"status": 0, "created_at": 0})
            return updated_product
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@app.delete("/products/{productId}", status_code=status.HTTP_200_OK)
async def delete_product_by_id(productId: str):
    isproductValid = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"})
    if isproductValid:
        deleted_product = await products_collection.update_one({"_id": ObjectId(productId)},
                                                               {"$set": {"status": "Deactivate"}})
        if deleted_product is not None and deleted_product.acknowledged:
            return {"detail": f"product deleted successfully with product id {productId}."}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreateDTO):
    product = jsonable_encoder(product)
    is_product_id_used = await products_collection.find_one({"email": product["productID"]})
    if not is_product_id_used:
        product["status"] = "Active"
        product["created_at"] = datetime.datetime.utcnow()
        new_product = await products_collection.insert_one(product)
        created_product = await products_collection.find_one({"_id": new_product.inserted_id},
                                                             {"status": 0, "created_at": 0})
        return created_product
    else:
        return {'detail': 'Product Id Already In Use. Please use Different Product ID.'}


@app.post("/users/{userId}/addItemToBucket", status_code=status.HTTP_201_CREATED)
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
                return await users_collection.find_one({"_id": ObjectId(userId)}, {"_id": 0, "bucket": 1})
            else:
                raise HTTPException(status.HTTP_404_NOT_FOUND,
                                    f"Requested quantities {quantity} of product {product_id} are not available. Max "
                                    f"Available Quantity is {fetchedProduct.quantity}.")
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Product exists with Product Id {product_id}.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.put("/users/{userId}/updateItemToBucket", response_model=List[BucketItem], status_code=status.HTTP_200_OK)
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
                        return await users_collection.find_one({"_id": ObjectId(userId)}, {"_id": 0, "bucket": 1})
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


@app.delete("/users/{userId}/deleteItemFromBucket", response_model=List[BucketItem], status_code=status.HTTP_200_OK)
async def delete_item_to_bucket(userId: str, productId: str):
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        for bucketItem in fetchedUser["bucket"]:
            if bucketItem.product_id == productId:
                users_collection.update_one({"_id": ObjectId(userId)},
                                            {"$pull": {"bucket": {"product_id": productId}}})
                return await users_collection.find_one({"_id": ObjectId(userId)}, {"_id": 0, "bucket": 1})
            else:
                raise HTTPException(status.HTTP_404_NOT_FOUND, f"Product Doesn't Exists In Bucket {productId}")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.delete("/users/{userId}/deleteBucket", status_code=status.HTTP_200_OK)
async def delete_bucket(userId: str):
    fetchedUser = await users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        if len(fetchedUser["bucket"]) != 0:
            for bucketItem in fetchedUser["bucket"]:
                users_collection.update_one({"_id": ObjectId(userId)},
                                            {"$pull": {"bucket": {"product_id": bucketItem["product_id"]}}})
            return {'detail': f'Bucket Deleted Successfully For User {userId}.'}
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Items In Bucket To Delete.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.get("/"
         "users/{userId}/getBucket", status_code=status.HTTP_200_OK)
async def get_bucket(userId: str):
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
            return bucket
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Items In Bucket.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.post("/users/{userId}/createOrder")
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
            return created_order
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Items In Bucket.")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User Id {userId}.")


@app.put("/orders/{orderId}")
async def update_order(orderId: str, order: OrderUpdateDTO):
    order = jsonable_encoder(order)
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        orders_collection.update_one({"_id": ObjectId(orderId)},
                                     {"$set": order})
        return await users_collection.find_one({"_id": ObjectId(orderId)})
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order Id {orderId}.")


@app.get("/orders")
async def get_all_orders():
    fetchedOrders = await orders_collection.find({}).to_list(1000)
    if fetchedOrders is not None:
        return fetchedOrders
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Orders exists .")


@app.get("/orders/{orderId}")
async def get_order_by_id(orderId: str):
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        return fetchedOrder
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order ID {orderId} .")


@app.delete("/orders/{orderId}")
async def delete_order(orderId: str):
    fetchedOrder = await orders_collection.find_one({"_id": ObjectId(orderId)})
    if fetchedOrder is not None:
        orders_collection.delete_one({"_id": ObjectId(orderId)})
        return {'detail': f'Order Deleted Successfully with Order ID {orderId}'}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Order exists with Order ID {orderId} .")


@app.get("/userId/{userId}/getAllOrders")
async def get_all_orders_for_user(userId: str):
    fetchedUser = users_collection.find_one({"_id": ObjectId(userId), "status": "Active"})
    if fetchedUser is not None:
        fetchedOrders = await orders_collection.find({"user_id": userId}).to_list(1000)
        if fetchedOrders is not None:
            return fetchedOrders
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"No Orders exists for User ID {userId} .")
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No User exists with User ID {userId} .")
