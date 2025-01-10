import string
import random
import joblib
import pymongo
import time
import pandas as pd
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier


if __name__ == "__main__":
    myclient = pymongo.MongoClient(config.MONGO_URL)
    mydb = myclient[config.DB_NAME]
    model = joblib.load(config.MODEL_PATH)

    patient_col = mydb["patients"]
    trees_col = mydb["trees"]