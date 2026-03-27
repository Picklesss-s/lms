import pandas as pd
from model import RiskClassifier
from lms_client import fetch_lms_data
from feature_manager import calculate_quiz_average, calculate_attendance_rate
import db_models

# Triggers an asynchronous sync of external LMS data and retrains the ML model
async def run_pipeline(db):
    print("Fetching dynamic data from Sample-LMS...")
    raw_data = await fetch_lms_data()

    # Extract the raw lists provided by the backend team
    students = raw_data['students']
    quizzes = raw_data['quizzes']
    attendance = raw_data['attendance']