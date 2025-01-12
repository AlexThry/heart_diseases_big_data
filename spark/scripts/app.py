from pyspark.sql import SparkSession
import joblib
import pandas as pd

print("Starting")

# Create Spark Session
spark = SparkSession.builder \
    .appName("Spark-MongoDB") \
    .config("spark.mongodb.input.uri", "mongodb://mongo_container:27017/heart_diseases.patients") \
    .config("spark.mongodb.output.uri", "mongodb://mongo_container:27017/heart_diseases.processed_patients") \
    .getOrCreate()

print("Connection set successfully!")
# Load Data from MongoDB
df = spark.read.format("mongodb").load().limit(10)

print("Data extracted correctly")
# Transform Data (Example: Predict Output)
pandas_df = df.toPandas()
X = pandas_df.drop(columns=["output"])  # Drop the output column if it exists

# Load pretrained model
model = joblib.load("/opt/spark/models/random_forest_model.pkl")

print("Model loaded!")
# Make Predictions
pandas_df["predictions"] = model.predict(X)

print("Predictions finished!")
# Save Back to MongoDB
completed_df = spark.createDataFrame(pandas_df)
completed_df.write.format("mongodb").mode("overwrite").save()
print("Data loaded successfully!")

spark.stop()
