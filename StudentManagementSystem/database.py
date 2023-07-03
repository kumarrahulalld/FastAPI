from motor import motor_asyncio

DATABASE_URL = "mongodb://localhost:27017"
client = motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client.SMS
student_collection = db.get_collection("student")