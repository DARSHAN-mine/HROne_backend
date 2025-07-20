# db.py
import motor.motor_asyncio
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()  # load env variables from .env

MONGO_URL = os.getenv("MONGO_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.ecommerce  # 'ecommerce' is our DB name

# Collections
product_collection = db.products
order_collection = db.orders



# product_collection = db["products"]
# order_collection = db["orders"]  # 👈 Add this line
