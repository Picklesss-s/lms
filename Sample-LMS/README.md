# Setup Guide: Sample LMS & Integration

This project contains a **Sample-LMS** (simulating an external system) and integrates it with the main AI backend.

## Prerequisites

*   Python 3.10+
*   Node.js & npm

## 1. Setup Sample-LMS (External System)

The Sample LMS mimics a real-world system storing granular data (quizzes, attendance, video clicks).

1.  Navigate to the folder:
    ```bash
    cd Sample-LMS
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Generate synthetic data (Seeds the database):
    ```bash
    python generate_raw_data.py
    ```

4.  Run the Service (Port 8001):
    ```bash
    uvicorn main:app --port 8001
    ```
    *Keep this terminal open.*

## 2. Setup AI Backend (Main System)

The backend pulls data from Sample-LMS to train the risk model.

1.  Navigate to the backend folder (new terminal):
    ```bash
    cd backend
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the Backend (Port 8000):
    ```bash
    uvicorn main:app --port 8000
    ```
    *Keep this terminal open.*

## 3. Setup Frontend

1.  Navigate to the frontend folder (new terminal):
    ```bash
    cd frontend
    ```

2.  Install & Run:
    ```bash
    npm install
    npm run dev
    ```

## 4. How to Sync Data

1.  Open the Instructor Dashboard in your browser (`http://localhost:5173`).
2.  Click the **"Sync with LMS"** button.
3.  The backend will:
    *   Fetch raw data from Sample-LMS (Port 8001).
    *   Aggregate it into risk features.
    *   Retrain the Risk Model.
    *   Update the dashboard with new predictions.
