import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/")
DB_NAME = os.getenv("DB_NAME", "heart_diseases")

MODEL_PATH = os.getenv("MODEL_PATH", "./random_forest_model.pkl")
DATASET_PATH = os.getenv("DATASET_PATH", "../data/heart_dataset.csv")

COOLDOWN = int(os.getenv("COOLDOWN", 60))
