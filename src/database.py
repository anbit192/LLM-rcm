import pymongo
from bson import ObjectId
from config import MONGODB_URL

mongo_cli = pymongo.MongoClient(MONGODB_URL)

db = mongo_cli["movies_LLM"]
user_col = db["users"]
rate_col = db["user_rates"]

# user = UserInfo(email="testuser@example.com", username="TestUser")


