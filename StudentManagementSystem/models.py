from pydantic import BaseModel
from typing import List
from bson import ObjectId


class Address(BaseModel):
    city: str
    country: str


class Social(BaseModel):
    type: str
    link: str


class Student(BaseModel):
    first_name: str
    last_name: str
    age: int
    address: Address
    phone_number: List[int]
    socials: List[Social]
