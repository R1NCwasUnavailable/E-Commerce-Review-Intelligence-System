import os
import re
from pathlib import Path
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Global dictionary to hold models
models = {}

# Path to fine-tuned model
FINE_TUNED_MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "mlops" / "fine_tuned_model"

# Common product aspects to look for
ASPECTS = ["battery", "camera", "display", "screen", "price", "performance", "build", "quality", "design", "software", "ui"]

def init_models():
    """Initialize ML models. Prefers fine-tuned model if available, falls back to default."""
    if "sentiment_classifier" not in models:
        device = 0 if torch.cuda.is_available() else -1
        
        if FINE_TUNED_MODEL_PATH.exists() and (FINE_TUNED_MODEL_PATH / "model.safetensors").exists():
            print(f"Loading fine-tuned model from {FINE_TUNED_MODEL_PATH}")
            tokenizer = AutoTokenizer.from_pretrained(str(FINE_TUNED_MODEL_PATH))
            model = AutoModelForSequenceClassification.from_pretrained(str(FINE_TUNED_MODEL_PATH))
            models["sentiment_classifier"] = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                device=device
            )
        else:
            print("Fine-tuned model not found. Using default distilbert-base-uncased-finetuned-sst-2-english.")
            models["sentiment_classifier"] = pipeline("sentiment-analysis", device=device)
        
        # Load T5 explicitly instead of via pipeline
        print("Loading T5 model for summarization...")
        models["t5_tokenizer"] = AutoTokenizer.from_pretrained("t5-small")
        # Ensure we move the model to the appropriate device
        t5_model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
        if device == 0:
            t5_model = t5_model.to("cuda")
        models["t5_model"] = t5_model


def _normalize_sentiment(label: str) -> str:
    """Normalize sentiment labels from different model outputs to standard labels."""
    label = label.lower().strip()
    if label in ("positive", "label_2"):
        return "positive"
    elif label in ("negative", "label_0"):
        return "negative"
    else:
        return "neutral"


def extract_aspect_sentiments(text: str):
    aspects = {}
    sentences = re.split(r'[.!?,;]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        found_aspects = [aspect for aspect in ASPECTS if aspect in sentence.lower()]
        if found_aspects:
            result = models["sentiment_classifier"](sentence)[0]
            sentiment_label = _normalize_sentiment(result["label"])
                
            for aspect in found_aspects:
                aspects[aspect] = sentiment_label
                
    return aspects


def analyze_text(text: str):
    """Perform overall sentiment + aspect-based sentiment analysis."""
    init_models()  # Ensure models are loaded
    
    result = models["sentiment_classifier"](text)[0]
    overall_sentiment = _normalize_sentiment(result["label"])

    aspects = extract_aspect_sentiments(text)

    return {
        "sentiment": overall_sentiment,
        "score": float(result["score"]),
        "aspects": aspects
    }


def summarize_reviews(reviews_text: list):
    """Generate a summary of multiple reviews using T5."""
    init_models()  # Ensure models are loaded
    
    if not reviews_text:
        return "No reviews to summarize."
    
    combined_text = " ".join(reviews_text)
    
    words = combined_text.split()
    if len(words) > 400:
        combined_text = " ".join(words[:400])
        
    input_text = "summarize: " + combined_text
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        inputs = models["t5_tokenizer"](input_text, return_tensors="pt", truncation=True, max_length=512)
        if device == "cuda":
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
        outputs = models["t5_model"].generate(
            **inputs, 
            max_new_tokens=50, 
            min_length=10, 
            do_sample=False
        )
        return models["t5_tokenizer"].decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print("Summarization error:", e)
        return "Could not generate summary."