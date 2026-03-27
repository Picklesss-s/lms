from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from sqlalchemy.orm import Session
from database import engine, get_db
import db_models

# Initialize the main FastAPI application instance
app = FastAPI(title="AI-LMS Backend API")

# Allow cross-origin requests from the frontend application
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-LMS API"}

# Creates all defined database tables when the API starts
@app.on_event("startup")
def startup():
    db_models.Base.metadata.create_all(bind=engine)

@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    # Returns all student records from the database
    return db.query(db_models.Student).all()