from app.services.sentiment_service import analyze_text, summarize_reviews

if __name__ == "__main__":
    print("Testing analyze_text with fine-tuned model...")
    sample_review = "The battery life is amazing but the camera is quite bad in low light."
    result = analyze_text(sample_review)
    print("Analyze Result:", result)
    
    print("\nTesting summarize_reviews...")
    reviews = [
        "The battery life is amazing but the camera is quite bad in low light.",
        "Great phone for the price, battery lasts two days.",
        "Camera could be better, but overall decent performance."
    ]
    summary = summarize_reviews(reviews)
    print("Summary:", summary)
    print("\nAll tests completed.")
