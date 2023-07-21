from pydantic import BaseModel, Field
from typing import Optional
from typing import List
from datetime import date, datetime


class Address(BaseModel):
    address1: Optional[str]
    address2: Optional[str]
    address3: Optional[str]
    locality: Optional[str]
    landmark: Optional[str]
    city: str
    state: str
    country: str
    pincode: int
    address_type: str
    phone_number: Optional[int]
    lat: Optional[float]
    long: Optional[float]
    is_default_address: bool


class BucketItem(BaseModel):
    product_id: str
    quantity: int


class User(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, description='First Name Should Be 2-50 characters Long.')
    last_name: str = Field(min_length=2, max_length=50, description='Second Name Should Be 2-50 characters Long.')
    email: str
    phone: int
    address: List[Address]
    bucket: List[BucketItem]
    orders: List[str]
    gender: str
    created_at: datetime
    dob: date
    status: str
    user_type: str


class UserUpdateDTO(BaseModel):
    first_name: Optional[str] = Field(min_length=2, max_length=50, description='First Name Should Be 2-50 characters '
                                                                               'Long.')
    last_name: Optional[str] = Field(min_length=2, max_length=50, description='Second Name Should Be 2-50 characters '
                                                                              'Long.')
    phone: Optional[int]
    address: Optional[List[Address]]
    gender: Optional[str]
    dob: Optional[date]


class UserCreateDTO(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, description='First Name Should Be 2-50 characters Long.')
    last_name: str = Field(min_length=2, max_length=50, description='Second Name Should Be 2-50 characters Long.')
    email: str
    phone: int
    address: List[Address]
    gender: str
    dob: date


class Review(BaseModel):
    user_id: str
    rating: int
    review_text: str


class Product(BaseModel):
    name: str
    productID: str
    description: Optional[str]
    category: str
    quantity: int
    price: float
    discount: Optional[float]
    rating: Optional[float]
    reviews: Optional[List[Review]]
    brand_name: str
    status: str
    created_at: datetime


class ProductUpdateDTO(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    quantity: Optional[int] = Field(default=0, ge=0)
    price: Optional[float] = Field(default=0.0, ge=0.0)
    discount: Optional[float] = Field(default=0.0, ge=0.0)
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    reviews: Optional[List[Review]]
    brand_name: Optional[str]


class ProductCreateDTO(BaseModel):
    name: Optional[str]
    productID: str
    description: Optional[str]
    category: Optional[str]
    quantity_available: Optional[int] = Field(default=0, ge=0)
    price: Optional[float] = Field(default=0.0, ge=0.0)
    discount: Optional[float] = Field(default=0.0, ge=0.0)
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    reviews: Optional[List[Review]]
    brand_name: Optional[str]


class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(default=1, gt=0)
    price: float = Field(ge=0.0)
    discount: float = Field(ge=0.0)
    TotalPrice: float = Field(ge=0.0)
    TotalDiscount: float = Field(ge=0.0)
    priceToPay: float = Field(ge=0.0)


class Order(BaseModel):
    user_id: str
    items: List[OrderItem]
    total_price: float
    total_discount: float
    price_to_pay: float
    delivery_address: Address
    received_by: Optional[str]
    status: str
    mode_of_payment: Optional[str]
    ordered_date: datetime
    delivery_date: Optional[datetime]
    transactionID: Optional[str]


class OrderUpdateDTO(BaseModel):
    delivery_address: Optional[Address]
    received_by: Optional[str]
    status: Optional[str]
    mode_of_payment: Optional[str]
    delivery_date: Optional[datetime]
    transactionID: Optional[str]
