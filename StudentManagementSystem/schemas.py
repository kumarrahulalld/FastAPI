from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId


class Address(BaseModel):
    city: str
    country: str


class Social(BaseModel):
    type: str
    link: str


class StudentCreateRequest(BaseModel):
    first_name: str
    last_name: str
    age: int
    address: Address
    phone_number: List[int]
    socials: List[Social]


class StudentUpdateRequest(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    address: Optional[Address]
    phone_number: Optional[List[int]]
    socials: Optional[List[Social]]
