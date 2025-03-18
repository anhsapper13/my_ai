from pydantic import BaseModel
from typing import List, Optional
from app.appointment_models import appointments_collection # Adjust import as needed
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import traceback
from bson import ObjectId

class Recommendation(BaseModel):
    service_id: str
    count: int
    
def get_user_recommendations(user_id: str, min_similar_users: int = 3) -> List[dict]:
    try:
        # Fetch user's booked services
        user_id_obj = ObjectId(user_id)
        print(f"Converted user_id to ObjectId: {user_id_obj}")  # Debug
        # Fetch user's booked services
        booked_services = [
            str(doc["service_id"])
            for doc in appointments_collection.find(
                {"user_id": user_id_obj, "status": {"$in": ["completed", "confirmed"]}}
            )
        ]
        print(f"Booked services for {user_id}: {booked_services}")

        pipeline = [
            {"$match": {"status": {"$in": ["completed", "confirmed"]}}},
            {"$group": {"_id": {"user_id": "$user_id", "service_id": "$service_id"}, "count": {"$sum": 1}}}
        ]
        interactions = list(appointments_collection.aggregate(pipeline))
        print("Interactions:", interactions)

        if not interactions:
            popularity_pipeline = [
                {"$match": {"status": {"$in": ["completed", "confirmed"]}}},
                {"$group": {"_id": "$service_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            popular_services = list(appointments_collection.aggregate(popularity_pipeline))
            return [{"service_id": str(doc["_id"]), "count": doc["count"]} for doc in popular_services]

        df_interactions = pd.DataFrame(interactions)
        df_interactions['user_id'] = df_interactions['_id'].apply(lambda x: str(x['user_id']))
        df_interactions['service_id'] = df_interactions['_id'].apply(lambda x: str(x['service_id']))
        print(f"Interactions: {df_interactions[['user_id', 'service_id', 'count']].to_dict(orient='records')}")  # Debug

        user_service_matrix = df_interactions.pivot_table(
            index="user_id",
            columns="service_id",
            values="count",
            fill_value=0
        )

        user_sim = cosine_similarity(user_service_matrix)
        user_sim_df = pd.DataFrame(user_sim, index=user_service_matrix.index, columns=user_service_matrix.index)

        if str(user_id) not in user_sim_df.index:
            popularity_pipeline = [
                {"$match": {"status": {"$in": ["completed", "confirmed"]}}},
                {"$group": {"_id": "$service_id", "count": {"$sum": 1}}},
                {"$match": {
                    "_id": {"$nin": booked_services}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            popular_services = list(appointments_collection.aggregate(popularity_pipeline))
            print("Popular Services:", popular_services)
            return [{"service_id": str(doc["_id"]), "count": doc["count"]} for doc in popular_services]

        similar_users = user_sim_df[str(user_id)][user_sim_df[str(user_id)] > 0.4].sort_values(ascending=False).index[1:]
        if len(similar_users) < min_similar_users:
            similar_users = user_sim_df[str(user_id)][user_sim_df[str(user_id)] > 0.2].sort_values(ascending=False).index[1:]
            if len(similar_users) == 0:
                similar_users = user_sim_df[str(user_id)].sort_values(ascending=False).index[1:5]

        similar_user_data = df_interactions[df_interactions["user_id"].isin(similar_users)]
        service_counts = similar_user_data.groupby("service_id")["count"].sum().reset_index()

        if booked_services:
            service_counts = service_counts[~service_counts["service_id"].isin(booked_services)]
            print(f"After filtering booked services: {service_counts.to_dict(orient='records')}")  # Debug
        print(f"Booked services for {user_id}: {booked_services}")
                    
        recommended_services = service_counts.sort_values(by="count", ascending=False).head(10)
        print("Recommended Services:", recommended_services)
        return recommended_services.to_dict(orient="records")

    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        traceback.print_exc()
        return []