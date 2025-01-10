import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "heart_diseases")

COOLDOWN = int(os.getenv("COOLDOWN", 60))
