from fastapi import FastAPI
from app.routes import router
from pymongo import MongoClient
import os
import certifi
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://minh:minhminh@cluster0.fm3vl.mongodb.net/Anhminh?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["Anhminh"]

app = FastAPI()
app.include_router(router)
@app.get("/")
def read_root():
    return {"message": "Hello, MongoDB!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)