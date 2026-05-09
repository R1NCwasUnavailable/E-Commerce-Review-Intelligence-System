from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.models.review import ReviewRequest, ReviewResponse, BulkReviewRequest, SummaryResponse, StatsResponse, FeedbackRequest
from app.services.sentiment_service import analyze_text, summarize_reviews
from app.database.mongo import review_collection
from bson import ObjectId

router = APIRouter()

@router.post("/analyze", response_model=ReviewResponse)
def analyze_single_review(request: ReviewRequest):
    try:
        analysis = analyze_text(request.text)
        
        # Save to DB
        document = {
            "text": request.text,
            "sentiment": analysis["sentiment"],
            "score": analysis["score"],
            "aspects": analysis["aspects"]
        }
        result = review_collection.insert_one(document)
        
        return ReviewResponse(
            id=str(result.inserted_id),
            text=request.text,
            sentiment=analysis["sentiment"],
            score=analysis["score"],
            aspects=analysis["aspects"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/bulk", response_model=List[ReviewResponse])
def analyze_bulk_reviews(request: BulkReviewRequest):
    try:
        responses = []
        documents = []
        for text in request.reviews:
            analysis = analyze_text(text)
            doc = {
                "text": text,
                "sentiment": analysis["sentiment"],
                "score": analysis["score"],
                "aspects": analysis["aspects"]
            }
            documents.append(doc)
        
        if documents:
            result = review_collection.insert_many(documents)
            for i, doc in enumerate(documents):
                responses.append(ReviewResponse(
                    id=str(result.inserted_ids[i]),
                    text=doc["text"],
                    sentiment=doc["sentiment"],
                    score=doc["score"],
                    aspects=doc["aspects"]
                ))
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
def get_statistics():
    try:
        total_reviews = review_collection.count_documents({})
        
        pipeline = [
            {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
        ]
        sentiment_counts = list(review_collection.aggregate(pipeline))
        
        distribution = {"positive": 0, "negative": 0, "neutral": 0}
        for item in sentiment_counts:
            if item["_id"] in distribution:
                distribution[item["_id"]] = item["count"]
                
        return StatsResponse(
            total_reviews=total_reviews,
            sentiment_distribution=distribution
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=SummaryResponse)
def get_summary():
    try:
        # Fetch up to 50 recent reviews
        reviews = list(review_collection.find().sort("_id", -1).limit(50))
        texts = [r["text"] for r in reviews]
        
        summary_text = summarize_reviews(texts)
        return SummaryResponse(summary=summary_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aspects")
def get_aspect_stats():
    try:
        # Aggregate aspect sentiments
        reviews = review_collection.find({}, {"aspects": 1})
        aspect_stats = {}
        
        for review in reviews:
            aspects = review.get("aspects", {})
            for aspect, sentiment in aspects.items():
                if aspect not in aspect_stats:
                    aspect_stats[aspect] = {"positive": 0, "negative": 0, "neutral": 0}
                if sentiment in aspect_stats[aspect]:
                    aspect_stats[aspect][sentiment] += 1
                    
        return aspect_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    try:
        update_data = {"is_corrected": True}
        if request.corrected_sentiment:
            update_data["corrected_sentiment"] = request.corrected_sentiment
        if request.corrected_aspects is not None:
            update_data["corrected_aspects"] = request.corrected_aspects
            
        result = review_collection.update_one(
            {"_id": ObjectId(request.review_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        return {"message": "Feedback saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

