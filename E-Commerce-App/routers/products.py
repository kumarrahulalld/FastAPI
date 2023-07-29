from fastapi import APIRouter
from models import ProductCreateDTO, ProductUpdateDTO
from database import products_collection
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
    prefix="/products",
    tags=["products"], )


@router.get("/{productId}", status_code=status.HTTP_200_OK)
async def get_product_by_id(productId: str):
    if not ObjectId.is_valid(productId):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Provided Product Id {productId} Is not a valid Object ID.')
    cachedproduct = r.hget('products', f'{productId}')
    if cachedproduct is not None:
        return json_util.loads(cachedproduct)
    fetchedproduct = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"},
                                                        {"status": 0, "created_at": 0})
    if fetchedproduct is not None:
        r.hset('products', f'{productId}', json_util.dumps(fetchedproduct))
        r.expire('products', 300)
        return fetchedproduct
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@router.get("", status_code=status.HTTP_200_OK)
async def get_all_products():
    cachedproducts = r.hgetall('products')
    if len(cachedproducts) != 0:
        productlist =list()
        for key in cachedproducts.keys():
            productlist.append(json_util.loads(cachedproducts.get(key)))
        print(productlist)
        return productlist
    products = await products_collection.find({"status": "Active"}, {"status": 0, "created_at": 0}).to_list(1000)
    if products is None:
        raise HTTPException(status.HTTP_204_NO_CONTENT, 'No products Available.')
    else:
        for product in products:
            r.hset(f'products', f'{str(product["_id"])}', json_util.dumps(product))
        r.expire('products', 300)
        return products


@router.put("/{productId}", status_code=status.HTTP_200_OK)
async def update_product_by_id(productId: str, product: ProductUpdateDTO):
    if not ObjectId.is_valid(productId):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Provided Product Id {productId} Is not a valid Object ID.')
    product = jsonable_encoder(product)
    isproductValid = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"})
    if isproductValid:
        updated_product = await products_collection.update_one({"_id": ObjectId(productId)},
                                                               {"$set": product})
        if updated_product is not None and updated_product.acknowledged:
            updated_product = await products_collection.find_one({"_id": ObjectId(productId)},
                                                                 {"status": 0, "created_at": 0})
            r.hset('products',f'{productId}', json_util.dumps(updated_product))
            r.expire('products', 300)
            return updated_product
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@router.delete("/{productId}", status_code=status.HTTP_200_OK)
async def delete_product_by_id(productId: str):
    if not ObjectId.is_valid(productId):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f'Provided Product Id {productId} Is not a valid Object ID.')
    isproductValid = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"})
    if isproductValid:
        deleted_product = await products_collection.update_one({"_id": ObjectId(productId)},
                                                               {"$set": {"status": "Deactivate"}})
        if deleted_product is not None and deleted_product.acknowledged:
            r.hdel('products', f'{productId}')
            return {"detail": f"product deleted successfully with product id {productId}."}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreateDTO):
    product = jsonable_encoder(product)
    is_product_id_used = await products_collection.find_one({"email": product["productID"]})
    if not is_product_id_used:
        product["status"] = "Active"
        product["created_at"] = datetime.datetime.utcnow()
        new_product = await products_collection.insert_one(product)
        created_product = await products_collection.find_one({"_id": new_product.inserted_id},
                                                             {"status": 0, "created_at": 0})
        r.hset('products', f'{new_product.inserted_id}', json_util.dumps(created_product))
        r.expire('products', 300)
        return created_product
    else:
        return {'detail': 'Product Id Already In Use. Please use Different Product ID.'}
    
