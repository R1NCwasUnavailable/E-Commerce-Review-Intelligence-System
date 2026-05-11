# E-Commerce Review Intelligence System 🚀

An end-to-end, MLOps-driven full-stack application designed to automatically analyze and summarize e-commerce product reviews. 

This project goes beyond simple inference by implementing a **Data Flywheel architecture**. It captures manual corrections to model predictions, stores them in MongoDB, and leverages an automated PyTorch training script to continuously fine-tune the core NLP models.

## ✨ Key Features
* **Custom AI Inference:** Utilizes a fine-tuned **DistilBERT** (`distilbert-base-uncased`) for overall sentiment classification and Aspect-Based Sentiment Analysis (ABSA).
* **Abstractive Summarization:** Uses Google's **T5-small** model to read dozens of individual reviews and generate concise, human-like executive summaries.
* **Data Flywheel / Active Learning:** An interactive UI allows users to correct inaccurate sentiment predictions. These corrections are immediately persisted to the database and appended to public datasets (Amazon Polarity) for continuous model fine-tuning.
* **Modern Dashboard:** A sleek, glassmorphism-styled React frontend displaying real-time analytics, sentiment distribution donuts, and AI-generated insights.
* **Production-Ready Backend:** A high-performance FastAPI server utilizing advanced lifecycle management to lazy-load multi-gigabyte machine learning models strictly on startup.

## 🛠️ Tech Stack
* **Machine Learning:** PyTorch, Hugging Face Transformers, Datasets, Scikit-learn
* **Backend:** Python, FastAPI, Uvicorn
* **Frontend:** React (v19), React Router v7, Vite, Vanilla CSS (Glassmorphism UI)
* **Database & Ops:** MongoDB, Docker, Docker Compose

---

## 🚀 How to Run Locally

### Option A: Native Development (Best for Model Training)
Ensure you have **Python 3.10+**, **Node.js**, and a local instance of **MongoDB Community Server** running on port `27017`.

**1. Start the Backend API**
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

**2. Start the Frontend Dashboard**
```bash
cd frontend
npm install
npm run dev
```

**3. Train / Fine-Tune the Model**
With the database running, you can trigger the Data Flywheel script to fetch user corrections and fine-tune DistilBERT:
```bash
cd backend
python mlops/train.py
```

### Option B: Dockerized Production (Best for Deployment)
Ensure you have **Docker Desktop** installed. This runs the frontend, backend, and MongoDB completely isolated.
```bash
docker-compose up --build -d
```

---

## 🧠 Architecture Details
1. **`sentiment_service.py`**: Auto-detects if a custom model exists in `/backend/mlops/fine_tuned_model/`. If found, it intercepts the default Hugging Face pipeline and securely maps custom token logits.
2. **`train.py`**: Re-trains DistilBERT utilizing the `Trainer` API, applying `weight_decay`, padding limits, and early checkpoint saving based on `eval_loss`.
