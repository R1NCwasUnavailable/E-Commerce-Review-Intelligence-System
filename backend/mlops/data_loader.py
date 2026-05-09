import os
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "review_intelligence")

def fetch_flywheel_data():
    """
    Fetches all corrected reviews from the MongoDB instance to use for training.
    """
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Only fetch records that have been corrected by humans
        corrected_reviews = list(db.reviews.find({"is_corrected": True}))
        
        if not corrected_reviews:
            print("No corrected data found in MongoDB. Flywheel is empty.")
            return pd.DataFrame()
            
        data = []
        for review in corrected_reviews:
            data.append({
                "text": review["text"],
                # Use corrected sentiment if available, otherwise fallback
                "label": review.get("corrected_sentiment", review["sentiment"])
            })
            
        df = pd.DataFrame(data)
        print(f"Loaded {len(df)} user-corrected samples from MongoDB.")
        return df
        
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_flywheel_data()
    print(df.head())
