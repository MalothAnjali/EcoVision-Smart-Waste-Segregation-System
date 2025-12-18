# EcoVision - Smart Waste Segregation System

An intelligent waste classification system using deep learning to automatically categorize waste into Recyclable, Non-recyclable, Hazardous, and Organic categories.

## 🎯 Features

- **Real-time Classification**: Upload images or use webcam for instant waste classification
- **Color-coded Alerts**: Visual feedback with green, red, yellow, and blue indicators
- **Bounding Box Detection**: Clear visual identification of waste items
- **Confidence Scores**: See how confident the model is about its predictions
- **Modern UI**: Beautiful, responsive React interface with TailwindCSS

## 🏗️ Architecture

- **Frontend**: React 18 + Vite + TailwindCSS
- **Backend**: FastAPI + TensorFlow Lite
- **ML Model**: MobileNetV2 (Transfer Learning)

## 📁 Project Structure

```
Ecovision/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, utils
│   │   ├── ml/             # Model inference
│   │   └── main.py         # FastAPI app
│   ├── models/             # Trained models (.h5, .tflite)
│   ├── scripts/            # Training & preprocessing scripts
│   ├── requirements.txt
│   └── .env
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API calls
│   │   ├── utils/         # Helper functions
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── DataSet/               # Training data
├── notebooks/             # Jupyter notebooks for experiments
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- pip
- npm/yarn

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app/main.py
```

Backend runs on: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

## 📊 Dataset

Dataset="waste classification dataset" from kaggle
The dataset contains 4 categories:
- **Recyclable**: Plastic bottles, cans, paper, etc.
- **Non-recyclable**: Mixed waste, contaminated items
- **Hazardous**: Batteries, chemicals, paints, pesticides
- **Organic**: Food waste, biodegradable materials

## 🎓 Model Training

```bash
cd backend/scripts
python train_model.py
```

## 🔧 Configuration

Edit `backend/.env` for backend settings:
```
MODEL_PATH=models/waste_classifier.tflite
CONFIDENCE_THRESHOLD=0.7
```

## 📝 API Documentation

Once backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎨 Color Coding

- 🟢 **Green**: Recyclable waste
- 🔴 **Red**: Non-recyclable waste
- 🟡 **Yellow**: Hazardous waste
- 🔵 **Blue**: Organic waste

## 📈 Performance

- Model Size: ~10MB (TensorFlow Lite)
- Inference Time: ~100-200ms on CPU
- Accuracy: ~85-90% (depends on training)




