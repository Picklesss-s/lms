import httpx
import os
import asyncio

# The URL of the external Sample-LMS system running in Docker
LMS_URL = os.getenv("EXTERNAL_LMS_URL", "http://sample-lms:8001")

# Fetches all raw student profiles, quiz attempts, and attendance asynchronously from the LMS
async def fetch_lms_data():
    async with httpx.AsyncClient() as client:
        # First, we fetch all users from the generic /students endpoint
        users_resp = await client.get(f"{LMS_URL}/students")
        students = users_resp.json()

        all_quizzes = []
        all_attendance = []

        # Then, fetch the dynamic records for each student concurrently
        for student in students:
            sid = student['id']
            q_req, a_req = await asyncio.gather(
                client.get(f"{LMS_URL}/students/{sid}/quizzes"),
                client.get(f"{LMS_URL}/students/{sid}/attendance")
            )

            # The LMS returns a JSON array (list), not a dictionary
            if q_req.status_code == 200:
                all_quizzes.extend(q_req.json())
            if a_req.status_code == 200:
                all_attendance.extend(a_req.json())

        return {
            "students": students,
            "quizzes": all_quizzes,
            "attendance": all_attendance
        }