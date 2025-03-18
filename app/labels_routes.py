from fastapi import APIRouter
from app.classify_post import classify_question
from app.database import labels_collection, questions_collection
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api", tags=["labels"])

class RequestData(BaseModel):
    question: str

@router.post("/submit_question")
def submit_question(request: RequestData):
    print("request data:", request)  # Debug: In toàn bộ request
    status, label, score, reason = classify_question(request.question)
    doc = {
        "question": request.question,  # Lưu chuỗi question
        "label": label,
        "score": score,
        "status": status,
        "reason": reason,
        "created_at": datetime.utcnow()  # Thêm timestamp
    }
    print("doc:", doc)  # Debug: In dữ liệu trước khi lưu
    questions_collection.insert_one(doc)
    if status == "accepted":
        return {"status":"accepted","message": "Câu hỏi được đăng thành công", "label": label, "score": score}
    elif status == "pending":
        return {"status":"pending","message": "Câu hỏi cần admin duyệt", "label": label, "score": score}
    else:
        return {"status":"rejected","message": "Your questions is rejected", "label": label, "score": score}