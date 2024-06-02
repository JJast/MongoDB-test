from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime
import time
import matplotlib.pyplot as plt

# Initialize Faker
fake = Faker()

# Constants for the amounts of data to generate
NUM_USERS = 200
NUM_COURSES = 50
NUM_ENROLLMENTS_PER_USER = 2
NUM_LESSONS_PER_COURSE = 5
NUM_QUIZZES_PER_LESSON = 2
NUM_QUESTIONS_PER_QUIZ = 3

client = MongoClient('mongodb://localhost:27017/')
db = client['online_learning']

timings = []

def measure_time(operation_name, func):
    start_time = time.time()
    func()
    end_time = time.time()
    duration = end_time - start_time
    timings.append((operation_name, duration))
    print(f"{operation_name} took {duration:.2f} seconds")

def drop_collections():
    db.users.drop()
    db.courses.drop()
    db.enrollments.drop()
    db.lessons.drop()
    db.quizzes.drop()
    db.quiz_questions.drop()
    print("Collections dropped successfully")

def create_collections():
    # MongoDB automatically creates collections when you insert documents into them
    print("Collections will be created automatically")

def insert_users():
    users = []
    for _ in range(NUM_USERS):
        user = {
            "_id": fake.uuid4(),
            "name": fake.name(),
            "email": fake.email(),
            "role": random.choice(["student", "instructor"]),
            "enrolledCourses": []
        }
        users.append(user)
    db.users.insert_many(users)
    print("Users inserted successfully")

def retrieve_users():
    users = list(db.users.find())
    print(f"{len(users)} users retrieved successfully")
    return users

def insert_courses(users):
    for _ in range(NUM_COURSES):
        course = {
            "_id": fake.uuid4(),
            "title": fake.catch_phrase(),
            "description": fake.text(),
            "instructor": random.choice([user["_id"] for user in users if user["role"] == "instructor"]),
            "lessons": [],
            "enrollments": []
        }

        lessons = []
        for _ in range(NUM_LESSONS_PER_COURSE):
            lesson = {
                "_id": fake.uuid4(),
                "courseId": course["_id"],
                "title": fake.sentence(),
                "content": fake.text(),
                "quizzes": []
            }

            quizzes = []
            for _ in range(NUM_QUIZZES_PER_LESSON):
                quiz = {
                    "_id": fake.uuid4(),
                    "lessonId": lesson["_id"],
                    "title": fake.sentence(),
                    "questions": []
                }

                questions = []
                for _ in range(NUM_QUESTIONS_PER_QUIZ):
                    question = {
                        "_id": fake.uuid4(),
                        "quizId": quiz["_id"],
                        "text": fake.sentence(),
                        "options": [fake.word() for __ in range(4)],
                        "correctAnswer": fake.word()
                    }
                    questions.append(question)
                quiz["questions"] = [question["_id"] for question in questions]
                db.quiz_questions.insert_many(questions)
                quizzes.append(quiz)
            lesson["quizzes"] = [quiz["_id"] for quiz in quizzes]
            db.quizzes.insert_many(quizzes)
            lessons.append(lesson)
        course["lessons"] = [lesson["_id"] for lesson in lessons]
        db.lessons.insert_many(lessons)
        db.courses.insert_one(course)
    print("Courses, lessons, quizzes, and questions inserted successfully")

def generate_enrollments(users):
    enrollments = []
    for user in users:
        if user["role"] == "student":
            enrolled_courses = random.sample(list(db.courses.find()), NUM_ENROLLMENTS_PER_USER)
            for course in enrolled_courses:
                enrollment = {
                    "_id": fake.uuid4(),
                    "userId": user["_id"],
                    "courseId": course["_id"],
                    "enrollmentDate": fake.date_time_between(start_date="-2y", end_date="now"),
                    "progress": f"{random.randint(0, 100)}%"
                }
                user["enrolledCourses"].append(course["_id"])
                enrollments.append(enrollment)
            db.users.update_one({"_id": user["_id"]}, {"$set": {"enrolledCourses": user["enrolledCourses"]}})
    db.enrollments.insert_many(enrollments)
    print("Enrollments generated successfully")

def retrieve_courses():
    courses = list(db.courses.find())
    print(f"{len(courses)} courses retrieved successfully")
    return courses

# Test multiple data insertions
def test_multiple_insertions():
    users = []
    for _ in range(50):
        user = {
            "_id": fake.uuid4(),
            "name": fake.name(),
            "email": fake.email(),
            "role": random.choice(["student", "instructor"]),
            "enrolledCourses": []
        }
        users.append(user)
    db.users.insert_many(users)
    print("50 additional users inserted successfully")

# Test data edit
def test_data_edit():
    user_ids = [user["_id"] for user in db.users.find().limit(10)]
    for user_id in user_ids:
        new_email = fake.email()
        db.users.update_one({"_id": user_id}, {"$set": {"email": new_email}})
    print("10 users updated successfully")

def plot_timings(timings):
    operations = [t[0] for t in timings]
    durations = [t[1] for t in timings]
    
    plt.figure(figsize=(12, 6))
    plt.barh(operations, durations, color='skyblue')
    plt.xlabel('Time (seconds)')
    plt.title('Performance of MongoDB Database Operations')
    plt.grid(axis='x')
    plt.show()

def main():
    measure_time("Drop Collections", drop_collections)
    measure_time("Create Collections", create_collections)
    measure_time("Insert Users", insert_users)
    users = []
    measure_time("Retrieve Users", lambda: users.extend(retrieve_users()))
    measure_time("Insert Courses, Lessons, Quizzes, and Questions", lambda: insert_courses(users))
    measure_time("Generate Enrollments", lambda: generate_enrollments(users))
    measure_time("Retrieve Courses", retrieve_courses)
    measure_time("Test Multiple Insertions", test_multiple_insertions)
    measure_time("Test Data Edit", test_data_edit)
    plot_timings(timings)
    print('Performance test completed')

if __name__ == '__main__':
    main()
