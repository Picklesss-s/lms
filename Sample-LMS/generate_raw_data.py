import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import numpy as np
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)
db = SessionLocal()
NUM_STUDENTS = 200
DAYS_HISTORY = 30
TODAY = datetime.now().date()
FIRST_NAMES = ['Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Ethan', 'Sophia',
    'Mason', 'Isabella', 'William', 'Mia', 'James', 'Charlotte', 'Benjamin',
    'Amelia', 'Lucas', 'Harper', 'Henry', 'Evelyn', 'Alexander', 'Abigail',
    'Michael', 'Emily', 'Daniel', 'Elizabeth', 'Jacob', 'Sofia', 'Logan',
    'Avery', 'Jackson', 'Ella', 'Sebastian', 'Scarlett', 'Aiden', 'Grace',
    'Matthew', 'Chloe', 'Samuel', 'Victoria', 'David', 'Riley', 'Joseph',
    'Aria', 'Carter', 'Lily', 'Owen', 'Aurora', 'Wyatt', 'Zoey', 'John']
LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
    'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez',
    'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore',
    'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson', 'White', 'Harris',
    'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young',
    'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill',
    'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera',
    'Campbell', 'Mitchell', 'Carter', 'Roberts']


def create_resources_and_quizzes():
    """ Function: create_resources_and_quizzes """
    print('Creating Resources and Quizzes...')
    resources = []
    quizzes = []
    for i in range(1, 11):
        q = models.Quiz(title=f'Module {i} Quiz', max_score=100)
        db.add(q)
        quizzes.append(q)
    for i in range(1, 51):
        rtype = random.choice(['video', 'pdf'])
        r = models.Resource(title=f'Resource {i} ({rtype})', type=rtype)
        db.add(r)
        resources.append(r)
    db.commit()
    return quizzes, resources


def generate_student_history(student, profile, quizzes, resources):
    """ Function: generate_student_history """
    if profile == 'high':
        attendance_prob = 0.9
        avg_score = 90
        score_std = 5
        interactions_per_day = 5, 15
        avg_duration = 60
    elif profile == 'average':
        attendance_prob = 0.6
        avg_score = 75
        score_std = 10
        interactions_per_day = 2, 8
        avg_duration = 40
    else:
        attendance_prob = 0.2
        avg_score = 50
        score_std = 15
        interactions_per_day = 0, 3
        avg_duration = 20
    last_login_date = None
    for i in range(DAYS_HISTORY):
        day = TODAY - timedelta(days=i)
        if random.random() < attendance_prob:
            if last_login_date is None:
                last_login_date = day
            duration = int(np.random.normal(avg_duration, 10))
            duration = max(10, duration)
            att = models.Attendance(student_id=student.id, date=day,
                duration_minutes=duration)
            db.add(att)
            num_interactions = random.randint(*interactions_per_day)
            for _ in range(num_interactions):
                res = random.choice(resources)
                ts = datetime.combine(day, datetime.min.time()) + timedelta(
                    minutes=random.randint(0, duration))
                inter = models.Interaction(student_id=student.id,
                    resource_id=res.id, timestamp=ts)
                db.add(inter)
    for quiz in quizzes:
        if profile == 'at_risk' and random.random() < 0.3:
            continue
        attempts_count = 1
        if profile == 'at_risk' and random.random() < 0.5:
            attempts_count = random.randint(2, 4)
        elif profile == 'average' and random.random() < 0.3:
            attempts_count = random.randint(1, 2)
        for k in range(attempts_count):
            raw_score = np.random.normal(avg_score, score_std)
            if k > 0:
                raw_score += 10
            final_score = min(100, max(0, raw_score))
            q_date = TODAY - timedelta(days=random.randint(0, 29))
            qa = models.QuizAttempt(student_id=student.id, quiz_id=quiz.id,
                score=final_score, attempt_date=q_date)
            db.add(qa)


def main():
    """ Function: main """
    print('Generating raw data...')
    quizzes, resources = create_resources_and_quizzes()
    for i in range(NUM_STUDENTS):
        roll = random.random()
        if roll < 0.3:
            profile = 'high'
        elif roll < 0.7:
            profile = 'average'
        else:
            profile = 'at_risk'
        name = f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}'
        student = models.Student(id=1000 + i, name=name)
        db.add(student)
        db.commit()
        generate_student_history(student, profile, quizzes, resources)
        if i % 20 == 0:
            print(f'Generated {i} students...')
            db.commit()
    db.commit()
    print('Done!')


if __name__ == '__main__':
    main()
