import sqlite3

# Connect to SQLite database (it will create file automatically)
conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# 1️⃣ Create Tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS quiz (
    quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER,
    question_text TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    correct_option INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    quiz_id INTEGER,
    score INTEGER
)
''')

conn.commit()


# 2️⃣ Functions

def register_user():
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    print("User registered successfully!\n")


def add_quiz():
    quiz_name = input("Enter quiz name: ")
    cursor.execute("INSERT INTO quiz (quiz_name) VALUES (?)", (quiz_name,))
    conn.commit()
    print("Quiz added successfully!\n")


def add_question():
    cursor.execute("SELECT * FROM quiz")
    quizzes = cursor.fetchall()
    if not quizzes:
        print("No quizzes found! Add a quiz first.\n")
        return
    print("Available Quizzes:")
    for q in quizzes:
        print(f"{q[0]}. {q[1]}")
    quiz_id = int(input("Enter quiz ID to add question: "))
    question_text = input("Enter question text: ")
    option1 = input("Option 1: ")
    option2 = input("Option 2: ")
    option3 = input("Option 3: ")
    option4 = input("Option 4: ")
    correct_option = int(input("Correct option number (1-4): "))
    cursor.execute('''INSERT INTO questions
        (quiz_id, question_text, option1, option2, option3, option4, correct_option)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (quiz_id, question_text, option1, option2, option3, option4, correct_option))
    conn.commit()
    print("Question added successfully!\n")


def take_quiz():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("Users:")
    for u in users:
        print(f"{u[0]}. {u[1]}")
    user_id = int(input("Enter your user ID: "))

    cursor.execute("SELECT * FROM quiz")
    quizzes = cursor.fetchall()
    print("Quizzes:")
    for q in quizzes:
        print(f"{q[0]}. {q[1]}")
    quiz_id = int(input("Enter quiz ID to take: "))

    cursor.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    questions = cursor.fetchall()
    if not questions:
        print("No questions in this quiz!\n")
        return

    score = 0
    for q in questions:
        print("\n" + q[2])  # question_text
        print(f"1. {q[3]}")
        print(f"2. {q[4]}")
        print(f"3. {q[5]}")
        print(f"4. {q[6]}")
        ans = int(input("Your answer (1-4): "))
        if ans == q[7]:
            score += 1

    cursor.execute("INSERT INTO results (user_id, quiz_id, score) VALUES (?, ?, ?)", (user_id, quiz_id, score))
    conn.commit()
    print(f"\nQuiz completed! Your score: {score}/{len(questions)}\n")


def view_results():
    cursor.execute('''SELECT R.result_id, U.name, Q.quiz_name, R.score 
                      FROM results R
                      JOIN users U ON R.user_id = U.user_id
                      JOIN quiz Q ON R.quiz_id = Q.quiz_id''')
    results = cursor.fetchall()
    print("\nAll Results:")
    for r in results:
        print(f"Result ID: {r[0]}, User: {r[1]}, Quiz: {r[2]}, Score: {r[3]}")
    print()


# 3️⃣ Menu
while True:
    print("=== Quiz Management System ===")
    print("1. Register User")
    print("2. Add Quiz")
    print("3. Add Question")
    print("4. Take Quiz")
    print("5. View Results")
    print("6. Exit")

    choice = input("Enter your choice: ")
    print()
    if choice == '1':
        register_user()
    elif choice == '2':
        add_quiz()
    elif choice == '3':
        add_question()
    elif choice == '4':
        take_quiz()
    elif choice == '5':
        view_results()
    elif choice == '6':
        print("Goodbye!")
        break
    else:
        print("Invalid choice! Try again.\n")


