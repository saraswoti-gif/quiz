import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sqlite3
import matplotlib.pyplot as plt

# ---------------- Database Setup ----------------
conn = sqlite3.connect("ecoscore.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT
)
""")
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
cursor.execute("""
CREATE TABLE IF NOT EXISTS badges (
    user_id INTEGER,
    badge TEXT,
    date TEXT
)
""")
conn.commit()

# ---------------- Global Variables ----------------
current_user_id = None
current_user_name = ""

# ---------------- Functions ----------------
def calculate_score(travel, electricity, water, food):
    score = 0
    if travel in ["Walk","Bicycle"]: score +=0
    elif travel=="Bike": score+=10
    else: score+=25
    score += 0 if electricity<3 else 10 if electricity<=6 else 25
    score += 0 if water<150 else 10 if water<=250 else 25
    score += 0 if food=="Vegetarian" else 10 if food=="Mixed" else 25
    return score

def assign_badge(user_id):
    cursor.execute("SELECT SUM(eco_score) FROM daily_data WHERE user_id=?",(user_id,))
    cumulative = cursor.fetchone()[0] or 0
    if cumulative <=100: badge="EcoMaster"
    elif cumulative <=200: badge="Gold"
    elif cumulative <=300: badge="Silver"
    else: badge="Bronze"
    cursor.execute("INSERT INTO badges (user_id,badge,date) VALUES (?,?,?)",(user_id,badge,str(date.today())))
    conn.commit()
    return badge

def ai_suggestions(user_id):
    cursor.execute("SELECT eco_score FROM daily_data WHERE user_id=? ORDER BY date DESC LIMIT 7",(user_id,))
    data = cursor.fetchall()
    if not data: return "No data for suggestions yet."
    avg = sum([r[0] for r in data])/len(data)
    if avg>50: return "⚠ High impact! Reduce car travel & non-veg meals."
    elif avg>25: return "🙂 Good! Save electricity & water."
    else: return "🌿 Excellent! Keep eco-friendly habits!"

def save_daily_data(user_id, travel, electricity, water, food):
    score = calculate_score(travel,electricity,water,food)
    today = date.today()
    cursor.execute("INSERT INTO daily_data (user_id, travel_type, electricity, water, food, eco_score, date) VALUES (?,?,?,?,?,?,?)",
                   (user_id,travel,electricity,water,food,score,str(today)))
    conn.commit()
    badge = assign_badge(user_id)
    messagebox.showinfo("EcoScore Result",f"Today's Score: {score}/100\nBadge: {badge}\n\nAI Tip:\n{ai_suggestions(user_id)}")
    update_dashboard()

def show_trend_chart():
    global current_user_id
    if not current_user_id:
        messagebox.showerror("Error","Please login first")
        return
    cursor.execute("SELECT date, eco_score FROM daily_data WHERE user_id=? ORDER BY date",(current_user_id,))
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data","No EcoScore data to display.")
        return
    dates = [r[0] for r in data]
    scores = [r[1] for r in data]
    plt.figure(figsize=(8,4))
    plt.plot(dates,scores,marker='o',color='green')
    plt.title("EcoScore Over Time")
    plt.xlabel("Date")
    plt.ylabel("EcoScore (Lower is Better)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def update_dashboard():
    global current_user_id
    if current_user_id:
        cursor.execute("SELECT eco_score FROM daily_data WHERE user_id=? ORDER BY date DESC LIMIT 1",(current_user_id,))
        last_score = cursor.fetchone()
        eco_score_label.config(text=f"Latest EcoScore: {last_score[0] if last_score else 'N/A'}/100")
        cursor.execute("SELECT badge FROM badges WHERE user_id=? ORDER BY date DESC LIMIT 1",(current_user_id,))
        last_badge = cursor.fetchone()
        badge_label.config(text=f"Current Badge: {last_badge[0] if last_badge else 'N/A'}")
        ai_label.config(text=f"AI Suggestion: {ai_suggestions(current_user_id)}")

# ---------------- Register/Login ----------------
def register_gui():
    reg_win = tk.Toplevel(root)
    reg_win.title("Register")
    tk.Label(reg_win,text="Name:").grid(row=0,column=0)
    tk.Label(reg_win,text="Email:").grid(row=1,column=0)
    tk.Label(reg_win,text="Password:").grid(row=2,column=0)
    name_entry = tk.Entry(reg_win)
    email_entry = tk.Entry(reg_win)
    pass_entry = tk.Entry(reg_win,show="*")
    name_entry.grid(row=0,column=1)
    email_entry.grid(row=1,column=1)
    pass_entry.grid(row=2,column=1)
    def submit_reg():
        cursor.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",(name_entry.get(),email_entry.get(),pass_entry.get()))
        conn.commit()
        messagebox.showinfo("Success","Registration complete")
        reg_win.destroy()
    tk.Button(reg_win,text="Register",command=submit_reg).grid(row=3,column=0,columnspan=2,pady=5)

def login_gui():
    global current_user_id,current_user_name
    login_win = tk.Toplevel(root)
    login_win.title("Login")
    tk.Label(login_win,text="Email:").grid(row=0,column=0)
    tk.Label(login_win,text="Password:").grid(row=1,column=0)
    email_entry = tk.Entry(login_win)
    pass_entry = tk.Entry(login_win,show="*")
    email_entry.grid(row=0,column=1)
    pass_entry.grid(row=1,column=1)
    def submit_login():
        global current_user_id,current_user_name
        cursor.execute("SELECT id,name FROM users WHERE email=? AND password=?",(email_entry.get(),pass_entry.get()))
        user = cursor.fetchone()
        if user:
            current_user_id = user[0]
            current_user_name = user[1]
            messagebox.showinfo("Welcome",f"Hello {current_user_name}")
            login_win.destroy()
            update_dashboard()
        else:
            messagebox.showerror("Error","Invalid credentials")
    tk.Button(login_win,text="Login",command=submit_login).grid(row=2,column=0,columnspan=2,pady=5)

# ---------------- Daily Input ----------------
def daily_input_gui():
    global current_user_id
    if not current_user_id:
        messagebox.showerror("Error","Please login first")
        return
    input_win = tk.Toplevel(root)
    input_win.title("Daily Eco Data")
    tk.Label(input_win,text="Travel Type:").grid(row=0,column=0)
    travel_combo = ttk.Combobox(input_win,values=["Walk","Bicycle","Bike","Car"])
    travel_combo.grid(row=0,column=1)
    tk.Label(input_win,text="Electricity units:").grid(row=1,column=0)
    elec_entry = tk.Entry(input_win)
    elec_entry.grid(row=1,column=1)
    tk.Label(input_win,text="Water liters:").grid(row=2,column=0)
    water_entry = tk.Entry(input_win)
    water_entry.grid(row=2,column=1)
    tk.Label(input_win,text="Food Type:").grid(row=3,column=0)
    food_combo = ttk.Combobox(input_win,values=["Vegetarian","Mixed","Nonveg"])
    food_combo.grid(row=3,column=1)
    def submit_daily():
        try:
            electricity = float(elec_entry.get())
            water = float(water_entry.get())
        except:
            messagebox.showerror("Error","Enter valid numbers")
            return
        save_daily_data(current_user_id,travel_combo.get(),electricity,water,food_combo.get())
        input_win.destroy()
    tk.Button(input_win,text="Submit",command=submit_daily).grid(row=4,column=0,columnspan=2,pady=5)

# ---------------- Logout Function ----------------
def logout():
    global current_user_id, current_user_name
    current_user_id = None
    current_user_name = ""
    eco_score_label.config(text="Latest EcoScore: N/A")
    badge_label.config(text="Current Badge: N/A")
    ai_label.config(text="AI Suggestion: N/A")
    messagebox.showinfo("Logout", "You have been logged out successfully!")

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("Smart EcoScore Dashboard")
root.geometry("550x450")

dash_frame = tk.LabelFrame(root,text="Dashboard", padx=10,pady=10)
dash_frame.pack(padx=10,pady=10,fill="both",expand=True)

eco_score_label = tk.Label(dash_frame,text="Latest EcoScore: N/A",font=("Arial",12))
eco_score_label.pack(pady=5)
badge_label = tk.Label(dash_frame,text="Current Badge: N/A",font=("Arial",12))
badge_label.pack(pady=5)
ai_label = tk.Label(dash_frame,text="AI Suggestion: N/A",font=("Arial",12),wraplength=500,justify="left")
ai_label.pack(pady=5)

# ---------------- Main Buttons ----------------
tk.Button(root,text="Register",width=20,command=register_gui).pack(pady=5)
tk.Button(root,text="Login",width=20,command=login_gui).pack(pady=5)
tk.Button(root,text="Enter Daily Eco Data",width=25,command=daily_input_gui).pack(pady=5)
tk.Button(root,text="Show EcoScore Trend Chart",width=25,command=show_trend_chart).pack(pady=5)
tk.Button(root,text="Logout",width=20,command=logout).pack(pady=5)

root.mainloop()
