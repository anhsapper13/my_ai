from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.recommendation import get_user_recommendations

router = APIRouter(prefix="/api", tags=["recommendations"])

# Định nghĩa request body
class RecommendationRequest(BaseModel):
    booked_services: Optional[List[str]] = []

@router.post("/recommend/{user_id}")
def recommend_services(user_id: str, request: RecommendationRequest):
    print("User ID:", user_id)
    print("Booked Services:", request.booked_services)

    recommendations = get_user_recommendations(user_id, request.booked_services)
    return {"recommended_services": recommendations}

@router.get("/recommend/{user_id}")
def get_recommend_services(user_id: str):
    print("User ID:", user_id)
    recommendations = get_user_recommendations(user_id, [])
    return {"recommended_services": recommendations}
