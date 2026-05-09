import os
import sys
import torch
import pandas as pd
from pathlib import Path
from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    Trainer, 
    TrainingArguments
)
from sklearn.model_selection import train_test_split

# Resolve paths relative to this script's location
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent

# Add mlops dir to path so data_loader can be imported
sys.path.insert(0, str(SCRIPT_DIR))
from data_loader import fetch_flywheel_data

# Configuration
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = str(SCRIPT_DIR / "results")
FINE_TUNED_DIR = str(SCRIPT_DIR / "fine_tuned_model")
NUM_EPOCHS = 2
BATCH_SIZE = 16

def prepare_data():
    print("Loading public dataset (Amazon Polarity)...")
    amazon_dataset = load_dataset("amazon_polarity", split="train[:1000]")
    
    # Amazon Polarity labels: 1 = positive, 0 = negative
    def map_amazon_labels(example):
        return {
            "text": example["content"],
            "label_str": "positive" if example["label"] == 1 else "negative"
        }
        
    amazon_mapped = amazon_dataset.map(map_amazon_labels)
    df_public = amazon_mapped.to_pandas()[["text", "label_str"]]
    
    print("Loading flywheel (user-corrected) data...")
    df_flywheel = fetch_flywheel_data()
    
    if not df_flywheel.empty:
        df_public = pd.concat([df_public, df_flywheel.rename(columns={"label": "label_str"})], ignore_index=True)
        print(f"Combined public data with {len(df_flywheel)} flywheel samples.")
    else:
        print("No flywheel data available. Training on public data only.")
    
    # Map string labels to integers for training
    label2id = {"negative": 0, "neutral": 1, "positive": 2}
    df_public["label"] = df_public["label_str"].map(lambda x: label2id.get(x.lower(), 1))
    
    print(f"Total training samples: {len(df_public)}")
    
    # Split into train/val
    train_df, val_df = train_test_split(df_public, test_size=0.1, random_state=42)
    
    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)
    
    return train_dataset, val_dataset

def train():
    print("Preparing datasets...")
    train_dataset, val_dataset = prepare_data()
    
    print(f"Loading tokenizer and model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)
        
    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_val = val_dataset.map(tokenize_function, batched=True)
    
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, 
        num_labels=3,
        id2label={0: "negative", 1: "neutral", 2: "positive"},
        label2id={"negative": 0, "neutral": 1, "positive": 2}
    )
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        num_train_epochs=NUM_EPOCHS,
        weight_decay=0.01,
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
    )
    
    print("Starting training...")
    trainer.train()
    
    print(f"Saving final model to {FINE_TUNED_DIR}...")
    model.save_pretrained(FINE_TUNED_DIR)
    tokenizer.save_pretrained(FINE_TUNED_DIR)
    print(f"Training complete! Model saved to {FINE_TUNED_DIR}")

if __name__ == "__main__":
    train()
