import sys
import os
import random
from datetime import datetime, timedelta
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal, engine
import models


def seed_lms_users():
    """ Function: seed_lms_users """
    print('Seeding Sample-LMS with test users...')
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    quizzes = db.query(models.Quiz).all()
    if not quizzes:
        print('No quizzes found. Creating defaults...')
        for i in range(1, 6):
            db.add(models.Quiz(title=f'Module {i} Quiz', max_score=100))
        db.commit()
        quizzes = db.query(models.Quiz).all()
    resources = db.query(models.Resource).all()
    if not resources:
        print('No resources found. Creating defaults...')
        for i in range(1, 21):
            rtype = 'video' if i % 2 == 0 else 'pdf'
            db.add(models.Resource(title=f'Resource {i}', type=rtype))
        db.commit()
        resources = db.query(models.Resource).all()
    test_students = [{'id': 9001, 'name': 'Elena Rodriguez', 'quiz_avg':
        95.0, 'attendance_rate': 0.98, 'interactions_count': 230,
        'afk_rate': 0.05}, {'id': 9002, 'name': 'Jamal Washington',
        'quiz_avg': 75.0, 'attendance_rate': 0.85, 'interactions_count':
        120, 'afk_rate': 0.1}, {'id': 9003, 'name': 'Marcus Johnson',
        'quiz_avg': 55.0, 'attendance_rate': 0.6, 'interactions_count': 70,
        'afk_rate': 0.2}, {'id': 9004, 'name': 'Sarah Chen', 'quiz_avg':
        65.0, 'attendance_rate': 0.4, 'interactions_count': 35, 'afk_rate':
        0.3}, {'id': 9005, 'name': 'Priya Patel', 'quiz_avg': 80.0,
        'attendance_rate': 0.9, 'interactions_count': 200, 'afk_rate': 0.8}]
    for s_data in test_students:
        student = db.query(models.Student).filter(models.Student.id ==
            s_data['id']).first()
        if not student:
            student = models.Student(id=s_data['id'], name=s_data['name'])
            db.add(student)
            print(f"Created student {s_data['name']}")
        else:
            student.name = s_data['name']
            db.query(models.QuizAttempt).filter(models.QuizAttempt.
                student_id == student.id).delete()
            db.query(models.Attendance).filter(models.Attendance.student_id ==
                student.id).delete()
            db.query(models.Interaction).filter(models.Interaction.
                student_id == student.id).delete()
            db.query(models.ResourceLog).filter(models.ResourceLog.
                student_id == student.id).delete()
            print(f"Reset history for {s_data['name']}")
        db.commit()
        scores = np.random.normal(s_data['quiz_avg'], 5, 5)
        for i, score in enumerate(scores):
            final_score = min(100, max(0, score))
            qa = models.QuizAttempt(student_id=student.id, quiz_id=random.
                choice(quizzes).id, score=final_score, attempt_date=
                datetime.now() - timedelta(days=i * 5))
            db.add(qa)
        days = 30
        present_days = int(days * s_data['attendance_rate'])
        for i in range(days):
            if i < present_days:
                att = models.Attendance(student_id=student.id, date=
                    datetime.now().date() - timedelta(days=i),
                    duration_minutes=60)
                db.add(att)
        if present_days > 0:
            per_day = s_data['interactions_count'] // present_days
            for i in range(present_days):
                day = datetime.now().date() - timedelta(days=i)
                for _ in range(per_day):
                    res = random.choice(resources)
                    db.add(models.Interaction(student_id=student.id,
                        resource_id=res.id, timestamp=datetime.combine(day,
                        datetime.min.time())))
                    is_afk = random.random() < s_data['afk_rate']
                    db.add(models.ResourceLog(student_id=student.id,
                        resource_id=res.id, duration_seconds=600 if is_afk else
                        300, is_afk=is_afk, scroll_engagement_score=0.1 if
                        is_afk else 0.8, timestamp=datetime.combine(day,
                        datetime.min.time())))
        db.commit()
    print('✓ Sample-LMS seeded successfully.')


if __name__ == '__main__':
    seed_lms_users()
