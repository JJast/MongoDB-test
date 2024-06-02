from pymongo import MongoClient
from faker import Faker
import random
import time
import matplotlib.pyplot as plt
import pandas as pd

# Initialize Faker
fake = Faker()

# Constants for the amounts of data to generate
NUM_USERS = 10
NUM_COURSES = 20
NUM_LESSONS_PER_COURSE = 5
NUM_QUIZZES_PER_LESSON = 2
NUM_QUESTIONS_PER_QUIZ = 3
NUM_ENROLLMENTS_PER_USER = 2

client = MongoClient('mongodb://localhost:27017/')
db = client['online_learning']

timings = []

def edit_number_of_operations(multiplication=1):
    global NUM_USERS, NUM_COURSES, NUM_ENROLLMENTS_PER_USER, NUM_LESSONS_PER_COURSE, NUM_QUIZZES_PER_LESSON, NUM_QUESTIONS_PER_QUIZ

    NUM_USERS = NUM_USERS * multiplication
    NUM_COURSES = NUM_COURSES * multiplication
    # NUM_ENROLLMENTS_PER_USER = NUM_ENROLLMENTS_PER_USER * multiplication
    # NUM_LESSONS_PER_COURSE = NUM_LESSONS_PER_COURSE * multiplication
    # NUM_QUIZZES_PER_LESSON = NUM_QUIZZES_PER_LESSON * multiplication
    # NUM_QUESTIONS_PER_QUIZ = NUM_QUESTIONS_PER_QUIZ * multiplication

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

def read_all_data():
    users = list(db.users.find())
    courses = list(db.courses.find())
    enrollments = list(db.enrollments.find())
    lessons = list(db.lessons.find())
    quizzes = list(db.quizzes.find())
    quiz_questions = list(db.quiz_questions.find())
    print("All data read successfully")
    return users, courses, enrollments, lessons, quizzes, quiz_questions

def update_all_data():
    db.users.update_many({}, {"$set": {"email": fake.email()}})
    db.courses.update_many({}, {"$set": {"description": fake.text()}})
    db.enrollments.update_many({}, {"$set": {"progress": f"{random.randint(0, 100)}%"}})
    db.lessons.update_many({}, {"$set": {"content": fake.text()}})
    db.quizzes.update_many({}, {"$set": {"title": fake.sentence()}})
    db.quiz_questions.update_many({}, {"$set": {"text": fake.sentence()}})
    print("All data updated successfully")

def delete_all_data():
    db.users.delete_many({})
    db.courses.delete_many({})
    db.enrollments.delete_many({})
    db.lessons.delete_many({})
    db.quizzes.delete_many({})
    db.quiz_questions.delete_many({})
    print("All data deleted successfully")

def insert_all_data():
    insert_users()
    users = retrieve_users()
    insert_courses(users)
    generate_enrollments(users)

def plot_timings():
    operations, durations = zip(*timings)

    plt.figure(figsize=(12, 6))
    plt.barh(operations, durations, color='skyblue')
    plt.xlabel('Time (seconds)')
    plt.title('Performance of MongoDB Database Operations')
    plt.grid(axis='x')
    plt.show()

def save_timings_to_excel(filename="timings_.xlsx"):
    timings_df = pd.DataFrame(timings, columns=["Operation", "Duration (seconds)"])
    timings_df.to_excel(filename, index=False)
    print(f"Timings saved to {filename} successfully")

def main():
    multiplication = input("Enter how many times to multiply the amount of data: ")
    try:
        multiplication = int(multiplication)
    except:
        print("Intiger not provided")
    if not isinstance(multiplication, int):
        print("Provided multiplication factor is not an integer. Defaulting to 1.")
        multiplication = 1
    edit_number_of_operations(multiplication)

    measure_time("Drop Tables", drop_collections)
    measure_time("Create Tables", create_collections)
    measure_time("Insert All Data", insert_all_data)
    measure_time("Read All Data", read_all_data)
    measure_time("Update All Data", update_all_data)
    measure_time("Delete All Data", delete_all_data)
    
    print('Performance test completed')

    save_timings_to_excel("timings_MongoDB_{}.xlsx".format(multiplication))
    plot_timings()

if __name__ == '__main__':
    main()
