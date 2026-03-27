from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# SQLAlchemy model representing a student record in the database
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_at_risk = Column(Boolean, default=False)