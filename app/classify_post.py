from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="roberta-large-mnli")

from app.database import labels_collection
from app.database import thresholds_collection


# get threshold from db
def get_threshold_from_db():
    threshold = thresholds_collection.find_one()
    print("Threshold:", threshold)
    return threshold["min_accept_score"], threshold["min_pending_score"]

def get_labels_from_db():
    labels = list(labels_collection.find({}, {"_id": 0}))
    candidate_labels = [label["name"] for label in labels]
    allowed_labels = [label["name"] for label in labels if label["allowed"]]
    return candidate_labels, allowed_labels


def classify_question(question):
    candidate_labels, allowed_labels = get_labels_from_db()
    min_accept_score, min_pending_score = get_threshold_from_db()
    print("Candidate labels:", candidate_labels)
    print("Allowed labels:", allowed_labels)
    result = classifier(question, candidate_labels)
    print("Classification result:", result)
    top_label = result["labels"][0]
    top_score = result["scores"][0]
    if top_label not in allowed_labels:
        return "rejected", top_label, top_score, "Nhãn không được phép"
    elif top_score >= min_accept_score:
        return "accepted", top_label, top_score, "Câu hỏi được chấp nhận ngay"
    elif top_score >= min_pending_score:
        return "pending", top_label, top_score, "Cần admin duyệt"
    else:
        return "rejected", top_label, top_score, "Điểm quá thấp"

