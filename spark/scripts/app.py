from pyspark.sql import SparkSession
import joblib
import pandas as pd
from pyspark.sql import SQLContext
from pyspark import SparkConf, SparkContext

print("Starting")

spark = SparkSession.builder \
    .appName("Spark-MongoDB") \
    .config("spark.mongodb.input.uri", "mongodb://mongo_container:27017/heart_diseases.patients") \
    .config("spark.mongodb.output.uri", "mongodb://mongo_container:27017/heart_diseases.processed_patients") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .config("spark.mongodb.output.writeMethod", "insert") \
    .config("spark.mongodb.output.replaceDocument", "false") \
    .getOrCreate()

print("Connection set successfully!")

# Load Data from MongoDB
df = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
    .option("spark.mongodb.input.uri", "mongodb://localhost:27017/heart_diseases.patients") \
    .load().limit(5)

# Select specific columns from the dataframe
df_selected = df.select("age", "oldpeak", "thalach", "cp", "exang", "slope", "trestbps", "chol", "fbs", "restecg", "ca", "thal")

# Convert to pandas DataFrame
pandas_df = df_selected.toPandas()
print("Data extracted correctly")

print(pandas_df.head())
print(pandas_df.columns)
# Load pretrained model
# model = joblib.load("/opt/spark/models/random_forest_model.pkl")

X = pandas_df.copy()
model = joblib.load("../models/random_forest_model.pkl")
print("Model loaded!")

# Make Predictions
pandas_df["predictions"] = model.predict(X)

print("Predictions finished!")

# Save Back to MongoDB
completed_df = spark.createDataFrame(pandas_df)

# Write to MongoDB
completed_df.write.format("com.mongodb.spark.sql.DefaultSource") \
    .option("spark.mongodb.output.uri", "mongodb://localhost:27017/heart_diseases.processed_patients") \
    .mode("append") \
    .save()

print("Data loaded successfully!")

spark.stop()
