import re
from transformers import pipeline
import torch

# Global dictionary to hold models
models = {}

# Common product aspects to look for
ASPECTS = ["battery", "camera", "display", "screen", "price", "performance", "build", "quality", "design", "software", "ui"]

def init_models():
    if "sentiment_classifier" not in models:
        # In latest transformers, device=0 is valid, but we can also use device_map="auto" if accelerated
        device = 0 if torch.cuda.is_available() else -1
        models["sentiment_classifier"] = pipeline("sentiment-analysis", device=device)
        models["summarizer"] = pipeline("summarization", model="t5-small", device=device)

def extract_aspect_sentiments(text: str):
    aspects = {}
    # Split text into simple sentences roughly
    sentences = re.split(r'[.!?]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Check if any aspect is in the sentence
        found_aspects = [aspect for aspect in ASPECTS if aspect in sentence.lower()]
        if found_aspects:
            # Predict sentiment for this sentence
            result = models["sentiment_classifier"](sentence)[0]
            sentiment_label = result["label"].lower()
            if sentiment_label == "positive":
                sentiment_label = "positive"
            elif sentiment_label == "negative":
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
                
            for aspect in found_aspects:
                aspects[aspect] = sentiment_label
                
    return aspects

def analyze_text(text: str):
    # Overall sentiment
    result = models["sentiment_classifier"](text)[0]
    overall_sentiment = result["label"].lower()
    if overall_sentiment == "positive":
        overall_sentiment = "positive"
    elif overall_sentiment == "negative":
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    # Aspect-based sentiment
    aspects = extract_aspect_sentiments(text)

    return {
        "sentiment": overall_sentiment,
        "score": float(result["score"]),
        "aspects": aspects
    }

def summarize_reviews(reviews_text: list):
    if not reviews_text:
        return "No reviews to summarize."
    
    # Combine texts
    combined_text = " ".join(reviews_text)
    
    # Truncate if too long (t5-small max length is 512 tokens usually)
    # Simple word truncation
    words = combined_text.split()
    if len(words) > 400:
        combined_text = " ".join(words[:400])
        
    # t5-small requires 'summarize: ' prefix
    input_text = "summarize: " + combined_text
    
    try:
        summary_result = models["summarizer"](input_text, max_length=50, min_length=10, do_sample=False)
        return summary_result[0]['summary_text']
    except Exception as e:
        print("Summarization error:", e)
        return "Could not generate summary."