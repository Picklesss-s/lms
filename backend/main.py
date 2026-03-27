from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from sqlalchemy.orm import Session
from database import engine, get_db
import db_models
from fastapi import HTTPException
# We import the ML pipeline logic that your teammate is writing
import ingest_and_train
from auth_utils import verify_token



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
    
@app.post("/sync")
async def sync_lms_data(db: Session = Depends(get_db), auth: bool = Depends(verify_token)):
    # Triggers the Machine Learning pipeline, protected by a simple simulated Bearer token
    try:
        await ingest_and_train.run_pipeline(db)
        return {"status": "success", "message": "LMS sync complete. Models retrained."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))