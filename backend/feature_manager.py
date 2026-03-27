import pandas as pd

# Calculates the mean quiz score for a student given raw LMS quiz attempt objects
def calculate_quiz_average(quiz_attempts):
    if not quiz_attempts:
        return 0.0
    df = pd.DataFrame(quiz_attempts)
    return df['score'].mean()

# Calculates the overall attendance percentage for a student given raw LMS attendance records
def calculate_attendance_rate(attendance_records):
    if not attendance_records:
        return 0.0
    df = pd.DataFrame(attendance_records)
    # Count the number of "present" records compared to the total
    return (df['duration_minutes'] > 0).mean() * 100.0