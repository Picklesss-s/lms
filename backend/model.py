import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Initializes the main risk prediction machine learning model
class RiskClassifier:
    def __init__(self):
        # We start with a generic Random Forest to predict passing rates
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.trained = False
    
    def predict(self, features_df):
        if not self.trained:
            # If the model has no data yet, fallback to a basic rule
            return (features_df['quiz_avg'] < 60) | (features_df['attendance_rate'] < 75)

        ml_prediction = self.model.predict(features_df)

        # Create a hybrid prediction: the Random forest result, OR a hard failure on attendance
        is_at_risk = (ml_prediction == 1) | (features_df['attendance_rate'] < 75)
        return is_at_risk

    def train(self, X_train, y_train):
        if X_train.empty:
            return
        self.model.fit(X_train, y_train)
        self.trained = True
