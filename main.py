from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime

# Initialize Faker
fake = Faker()

# Constants for the amounts of data to generate
NUM_USERS = 100
NUM_COURSES = 20
NUM_ENROLLMENTS_PER_USER = 2
NUM_LESSONS_PER_COURSE = 5
NUM_QUIZZES_PER_LESSON = 2
NUM_QUESTIONS_PER_QUIZ = 3
NUM_SUBMISSIONS_PER_QUIZ = 50  # Total across all users, not per user

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['online_learning']

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
                "enrollmentDate": fake.past_date(),
                "progress": f"{random.randint(0, 100)}%"
            }
            user["enrolledCourses"].append(course["_id"])
            db.enrollments.insert_one(enrollment)
    db.users.update_one({"_id": user["_id"]}, {"$set": {"enrolledCourses": user["enrolledCourses"]}})

# Note: Submissions would be generated similarly based on the existing quizzes and users,
# and inserting them into the 'submissions' collection.

print("Random data generated and inserted into the database.")
