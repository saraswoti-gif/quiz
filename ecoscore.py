import sqlite3
from datetime import date
import matplotlib.pyplot as plt

# -------------------- Database Setup --------------------
conn = sqlite3.connect("ecoscore.db")
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")

# Daily data table
cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    travel_type TEXT,
    electricity REAL,
    water REAL,
    food TEXT,
    eco_score INTEGER,
    date TEXT
)
""")
# Gamification table
cursor.execute("""
CREATE TABLE IF NOT EXISTS badges (
    user_id INTEGER,
    badge TEXT,
    date TEXT
)
""")
conn.commit()

# -------------------- Functions --------------------

# Registration & Login
def register():
    print("\n--- User Registration ---")
    name = input("Name: ")
    email = input("Email: ")
    password = input("Password: ")
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
    conn.commit()
    print(f"✅ Registered! Welcome {name}")

def login():
    print("\n--- User Login ---")
    email = input("Email: ")
    password = input("Password: ")
    cursor.execute("SELECT id, name FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()
    if user:
        print(f"✅ Login successful! Welcome {user[1]}")
        return user[0], user[1]
    else:
        print("❌ Invalid email or password")
        return None, None

# EcoScore calculation
def calculate_score(travel, electricity, water, food):
    score = 0
    # Travel
    if travel.lower() in ["walk", "bicycle"]:
        score += 0
    elif travel.lower() == "bike":
        score += 10
    else:
        score += 25
    # Electricity
    if electricity < 3: score += 0
    elif electricity <= 6: score += 10
    else: score += 25
    # Water
    if water < 150: score += 0
    elif water <= 250: score += 10
    else: score += 25
    # Food
    if food.lower() == "vegetarian": score += 0
    elif food.lower() == "mixed": score += 10
    else: score += 25
    return score

# AI-powered suggestion
def ai_suggestions(user_id):
    cursor.execute("SELECT travel_type, electricity, water, food, eco_score FROM daily_data WHERE user_id=? ORDER BY date DESC LIMIT 7", (user_id,))
    data = cursor.fetchall()
    if not data:
        print("No past data for AI suggestions.")
        return
    avg_score = sum([row[4] for row in data])/len(data)
    print("\n--- AI Suggestions ---")
    if avg_score > 50:
        print("⚠ High impact! Try reducing car travel and non-veg meals this week.")
    elif avg_score > 25:
        print("🙂 Good! Focus on saving electricity and water slightly.")
    else:
        print("🌿 Excellent! Keep up your eco-friendly habits!")

# Gamification
def assign_badge(user_id, total_score):
    # Check total cumulative score
    cursor.execute("SELECT SUM(eco_score) FROM daily_data WHERE user_id=?", (user_id,))
    cumulative = cursor.fetchone()[0] or 0
    badge = None
    if cumulative <= 100:
        badge = "EcoMaster"
    elif cumulative <= 200:
        badge = "Gold"
    elif cumulative <= 300:
        badge = "Silver"
    else:
        badge = "Bronze"
    cursor.execute("INSERT INTO badges (user_id, badge, date) VALUES (?, ?, ?)", (user_id, badge, str(date.today())))
    conn.commit()
    print(f"🏅 You earned the badge: {badge}")

# Enter daily data
def enter_daily_data(user_id):
    print("\n--- Enter Daily Eco Data ---")
    travel = input("Travel (walk/bicycle/bike/car): ")
    electricity = float(input("Electricity units used today: "))
    water = float(input("Water liters used today: "))
    food = input("Food (vegetarian/mixed/nonveg): ")
    total_score = calculate_score(travel, electricity, water, food)
    today = date.today()
    cursor.execute("INSERT INTO daily_data (user_id, travel_type, electricity, water, food, eco_score, date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (user_id, travel, electricity, water, food, total_score, str(today)))
    conn.commit()
    print(f"Your EcoScore today: {total_score}/100")
    assign_badge(user_id, total_score)

# View history
def view_history(user_id):
    cursor.execute("SELECT date, travel_type, electricity, water, food, eco_score FROM daily_data WHERE user_id=? ORDER BY date", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        print("No data found.")
        return
    print("\n--- EcoScore History ---")
    for r in rows:
        print(f"Date: {r[0]}, Travel: {r[1]}, Electricity: {r[2]}, Water: {r[3]}, Food: {r[4]}, Score: {r[5]}")

# Show trend chart
def show_chart(user_id):
    cursor.execute("SELECT date, eco_score FROM daily_data WHERE user_id=? ORDER BY date", (user_id,))
    data = cursor.fetchall()
    if not data:
        print("No data to show.")
        return
    dates = [row[0] for row in data]
    scores = [row[1] for row in data]
    plt.plot(dates, scores, marker='o', linestyle='-', color='green')
    plt.title("Your EcoScore Over Time")
    plt.xlabel("Date")
    plt.ylabel("EcoScore (Lower is Better)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

# -------------------- Main Menu --------------------
while True:
    print("\n--- Smart EcoScore System ---")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    choice = input("Option: ")
    if choice == "1":
        register()
    elif choice == "2":
        user_id, name = login()
        if user_id:
            while True:
                print(f"\n--- Welcome {name} ---")
                print("1. Enter Today's Eco Data")
                print("2. View History")
                print("3. Show Trend Chart")
                print("4. AI Suggestions")
                print("5. Logout")
                action = input("Option: ")
                if action == "1":
                    enter_daily_data(user_id)
                elif action == "2":
                    view_history(user_id)
                elif action == "3":
                    show_chart(user_id)
                elif action == "4":
                    ai_suggestions(user_id)
                elif action == "5":
                    print("Logging out...")
                    break
                else:
                    print("Invalid option.")
    elif choice == "3":
        print("Goodbye! 🌱")
        break
    else:
        print("Invalid option.")

conn.close()
