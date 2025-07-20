# schemas.py
from pydantic import BaseModel, Field
from typing import List

class SizeModel(BaseModel):
    size: str
    quantity: int

class ProductModel(BaseModel):
    name: str
    price: float
    sizes: List[SizeModel]


class OrderedProduct(BaseModel):
    product_id: str
    size: str
    quantity: int

class OrderModel(BaseModel):
    user_id: str
    products: List[OrderedProduct]


class OrderItemModel(BaseModel):
    product_id: str
    quantity: int

class OrderRequestModel(BaseModel):
    user_id: str
    items: List[OrderItemModel]
