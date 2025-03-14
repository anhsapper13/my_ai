import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from app.appointment_models import appointments_collection
import traceback


def get_user_recommendations(user_id: str):
    """
    Get service recommendations for a user based on similar users' booking history.

    Args:
        user_id (str): The ID of the user to get recommendations for.
        booked_services (list): List of service IDs the user has already booked (optional).

    Returns:
        list: List of recommended services as dictionaries.
    """
    try:
        # Fetch user's booked services if not provided
     
        booked_services = [
                str(doc["service_id"])
                for doc in appointments_collection.find(
                    {"user_id": user_id, "status": {"$in": ["completed", "confirmed"]}}
                )
            ]

        # Aggregation pipeline for user-service interactions
        pipeline = [
            {"$match": {"status": {"$in": ["completed", "confirmed"]}}}, 
            {"$group": {"_id": {"user_id": "$user_id", "service_id": "$service_id"}, "count": {"$sum": 1}}}
        ]
        interactions = list(appointments_collection.aggregate(pipeline))

        if not interactions:
            return []

        # Convert to DataFrame
        df_interactions = pd.DataFrame(interactions)
        if df_interactions.empty:
            return []

        df_interactions['user_id'] = df_interactions['_id'].apply(lambda x: str(x['user_id']))
        df_interactions['service_id'] = df_interactions['_id'].apply(lambda x: str(x['service_id']))

        # Build user-service matrix
        user_service_matrix = df_interactions.pivot_table(
            index="user_id",
            columns="service_id",
            values="count",
            fill_value=0
        )

        # Compute cosine similarity
        user_sim = cosine_similarity(user_service_matrix)
        user_sim_df = pd.DataFrame(user_sim, index=user_service_matrix.index, columns=user_service_matrix.index)

        if user_id not in user_sim_df.index:
            return []

        # Get top 5-6 similar users
        similar_users = user_sim_df[user_id].sort_values(ascending=False).index[1:6]  # ✅ Tăng số lượng user tương tự
        # similar_users = user_sim_df[user_id][user_sim_df[user_id] > 0.5].sort_values(ascending=False).index[1:]

        # Aggregate services from similar users
        similar_user_data = df_interactions[df_interactions["user_id"].isin(similar_users)]
        service_counts = similar_user_data.groupby("service_id")["count"].sum().reset_index()

        # Filter out already booked services
        if booked_services:
            service_counts = service_counts[~service_counts["service_id"].isin(booked_services)]

        # Sort and limit to top 10
        recommended_services = service_counts.sort_values(by="count", ascending=False).head(10)

        return recommended_services.to_dict(orient="records")

    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        traceback.print_exc()  # ✅ In traceback để dễ debug
        return []
