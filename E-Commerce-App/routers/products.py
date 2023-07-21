from fastapi import APIRouter
from models import ProductCreateDTO, ProductUpdateDTO
from database import products_collection
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import datetime
import pydantic
from typing import List
from bson import ObjectId
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

router = APIRouter(
    prefix="",
    tags=["products"], )


@router.get("/products/{productId}", response_model=ProductCreateDTO, status_code=status.HTTP_200_OK)
async def get_product_by_id(productId: str):
    fetchedproduct = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"},
                                                        {"status": 0, "created_at": 0})
    if fetchedproduct is not None:
        return fetchedproduct
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@router.get("/products", response_model=List[ProductCreateDTO], status_code=status.HTTP_200_OK)
async def get_all_products():
    products = await products_collection.find({"status": "Active"}, {"status": 0, "created_at": 0}).to_list(1000)
    if products is None:
        raise HTTPException(status.HTTP_204_NO_CONTENT, 'No products Available.')
    else:
        return products


@router.put("/products/{productId}", response_model=ProductUpdateDTO, status_code=status.HTTP_200_OK)
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


@router.delete("/products/{productId}", status_code=status.HTTP_200_OK)
async def delete_product_by_id(productId: str):
    isproductValid = await products_collection.find_one({"_id": ObjectId(productId), "status": "Active"})
    if isproductValid:
        deleted_product = await products_collection.update_one({"_id": ObjectId(productId)},
                                                               {"$set": {"status": "Deactivate"}})
        if deleted_product is not None and deleted_product.acknowledged:
            return {"detail": f"product deleted successfully with product id {productId}."}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No product exists with product Id {productId}.")


@router.post("/products", status_code=status.HTTP_201_CREATED)
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
