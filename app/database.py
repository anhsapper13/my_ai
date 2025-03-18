from pymongo import MongoClient
import os
from dotenv import load_dotenv
import certifi

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://minh:minhminh@cluster0.fm3vl.mongodb.net/Anhminh?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["Anhminh"]

# appointments collection
appointments_collection = db["appointments"]
# labels collection
questions_collection = db["questions"]

# labels collection
labels_collection = db["labels"]
thresholds_collection = db["thresholds"]


