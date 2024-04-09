from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime

fake = Faker()

NUM_USERS = 100
NUM_COURSES = 20
NUM_ENROLLMENTS_PER_USER = 2
NUM_LESSONS_PER_COURSE = 5
NUM_QUIZZES_PER_LESSON = 2
NUM_QUESTIONS_PER_QUIZ = 3
NUM_SUBMISSIONS_PER_QUIZ = 50  # Total across all users, not per user

client = MongoClient('mongodb://localhost:27017/')
db = client['online_learning']

db.users.delete_many({})
db.courses.delete_many({})
db.enrollments.delete_many({})
db.lessons.delete_many({})
db.quizzes.delete_many({})
db.quiz_questions.delete_many({})
db.submissions.delete_many({})

# Generate Users
for _ in range(NUM_USERS):
    user = {
        "_id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "role": random.choice(["student", "instructor"]),
        "enrolledCourses": []
    }
    db.users.insert_one(user)

users = list(db.users.find())

# Generate Courses
for _ in range(NUM_COURSES):
    course = {
        "_id": fake.uuid4(),
        "title": fake.catch_phrase(),
        "description": fake.text(),
        "instructor": random.choice([user["_id"] for user in users if user["role"] == "instructor"]),
        "lessons": [],
        "enrollments": []
    }
    for _ in range(NUM_LESSONS_PER_COURSE):
        lesson = {
            "_id": fake.uuid4(),
            "courseId": course["_id"],
            "title": fake.sentence(),
            "content": fake.text(),
            "quizzes": []
        }
        for _ in range(NUM_QUIZZES_PER_LESSON):
            quiz = {
                "_id": fake.uuid4(),
                "lessonId": lesson["_id"],
                "title": fake.sentence(),
                "questions": []
            }
            for _ in range(NUM_QUESTIONS_PER_QUIZ):
                question = {
                    "_id": fake.uuid4(),
                    "quizId": quiz["_id"],
                    "text": fake.sentence(),
                    "options": [fake.word() for __ in range(4)],
                    "correctAnswer": fake.word()
                }
                quiz["questions"].append(question["_id"])
                db.quiz_questions.insert_one(question)
            lesson["quizzes"].append(quiz["_id"])
            db.quizzes.insert_one(quiz)
        course["lessons"].append(lesson["_id"])
        db.lessons.insert_one(lesson)
    db.courses.insert_one(course)

# Generate Enrollments
for user in users:
    if user["role"] == "student":
        enrolled_courses = random.sample(list(db.courses.find()), NUM_ENROLLMENTS_PER_USER)
        for course in enrolled_courses:
            enrollment = {
                "_id": fake.uuid4(),
                "userId": user["_id"],
                "courseId": course["_id"],
                # Using fake.date_between() to generate a datetime object in the past
                "enrollmentDate": fake.date_time_between(start_date="-2y", end_date="now"),
                "progress": f"{random.randint(0, 100)}%"
            }
            user["enrolledCourses"].append(course["_id"])
            db.enrollments.insert_one(enrollment)
    db.users.update_one({"_id": user["_id"]}, {"$set": {"enrolledCourses": user["enrolledCourses"]}})

print("Random data generated and inserted into the database.")
