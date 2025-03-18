from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as recommendation_router
from app.labels_routes import router as labels_router
from pymongo import MongoClient
import os
import certifi
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://minh:minhminh@cluster0.fm3vl.mongodb.net/Anhminh?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["Anhminh"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)


app.include_router(recommendation_router)
app.include_router(labels_router)

@app.get("/")
def read_root():
    return {"message": "Hello, MongoDB!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)