from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship, declarative_base
Base = declarative_base()


class Student(Base):
    """ Class: Student """
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quiz_attempts = relationship('QuizAttempt', back_populates='student',
        cascade='all, delete-orphan')
    attendance_records = relationship('Attendance', back_populates=
        'student', cascade='all, delete-orphan')
    interactions = relationship('Interaction', back_populates='student',
        cascade='all, delete-orphan')
    resource_logs = relationship('ResourceLog', back_populates='student',
        cascade='all, delete-orphan')


class Quiz(Base):
    """ Class: Quiz """
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    max_score = Column(Integer, default=100)


class QuizAttempt(Base):
    """ Class: QuizAttempt """
    __tablename__ = 'quiz_attempts'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    score = Column(Float)
    attempt_date = Column(DateTime)
    student = relationship('Student', back_populates='quiz_attempts')
    quiz = relationship('Quiz')


class Attendance(Base):
    """ Class: Attendance """
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    date = Column(Date)
    duration_minutes = Column(Integer)
    student = relationship('Student', back_populates='attendance_records')


class Resource(Base):
    """ Class: Resource """
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)


class Interaction(Base):
    """ Class: Interaction """
    __tablename__ = 'interactions'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    resource_id = Column(Integer, ForeignKey('resources.id'))
    timestamp = Column(DateTime)
    student = relationship('Student', back_populates='interactions')
    resource = relationship('Resource')


class ResourceLog(Base):
    """ Class: ResourceLog """
    __tablename__ = 'resource_logs'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    resource_id = Column(Integer, ForeignKey('resources.id'))
    duration_seconds = Column(Integer, default=0)
    scroll_engagement_score = Column(Float, default=0.0)
    is_afk = Column(Boolean, default=False)
    timestamp = Column(DateTime)
    student = relationship('Student', back_populates='resource_logs')
    resource = relationship('Resource')
