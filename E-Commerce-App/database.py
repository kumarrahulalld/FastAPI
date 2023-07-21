from motor import motor_asyncio

DATABASE_URL = "mongodb://localhost:27017"
client = motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client.ECommerce
users_collection = db.get_collection("users")
products_collection = db.get_collection("products")
orders_collection = db.get_collection("orders")