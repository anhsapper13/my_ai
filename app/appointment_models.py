from pymongo import MongoClient
import certifi
import os
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://minh:minhminh@cluster0.fm3vl.mongodb.net/Anhminh?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["Anhminh"]
appointments_collection = db["appointments"]