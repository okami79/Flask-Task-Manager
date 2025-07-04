import sqlite3
import secrets
from flask import render_template, url_for, Flask, request, redirect, flash
from datetime import datetime
from zoneinfo import ZoneInfo


def get_db():
    con = sqlite3.connect("task_database.db")
    return con

def init_table():
    with get_db() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0,
                category TEXT,
                date TEXT
            )
        """)

def AddTask(task, category=None):
    with get_db() as con:
        tasks = con.cursor()
        date = datetime.now(ZoneInfo("Asia/Kolkata")). strftime("%d-%b-%Y %H:%M")
        tasks.execute("INSERT INTO tasks(task, done, category, date) VALUES(?, 0, ?, ?)", (task, category, date))
    return

def MarkDone(taskno):
    with get_db() as con:
        tasks = con.cursor()
        tasks.execute("UPDATE tasks SET done = 1 WHERE id = ?", (taskno,))
    return

def DelTask(taskno):
    with get_db() as con:
        tasks = con.cursor()
        tasks.execute("DELETE FROM tasks WHERE id = ?", (taskno,))
    return

def UpdateTask(taskno, newtask, newcat = None):
    with get_db() as con:
        tasks = con.cursor()
        date = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%b-%y %H:%M")
        if not newcat:
            tasks.execute("SELECT category FROM tasks WHERE id = ?", (taskno,))
            (newcat,) = tasks.fetchone()
        tasks.execute("UPDATE tasks SET task = ?, category = ?, done = ?, date = ? WHERE id = ?", (newtask, newcat, 0, date, taskno))
    return

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route("/",  methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task = request.form.get("task")
        if request.form.get("cattext") and request.form.get("catdrop"):
            flash(f"Error! Please add a new task or select from a previous task", "error")
        else:
            category = request.form.get("cattext") or request.form.get("catdrop")
            AddTask(task, category)
    with get_db() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM tasks ORDER BY category")
        tasks = cur.fetchall()
        cur.execute("SELECT DISTINCT category FROM tasks")
        categories = cur.fetchall()
    return render_template("index.html", tasks = tasks, categories = categories)

@app.route("/delete/<int:taskno>")
def delete(taskno):
    try:
        DelTask(taskno)
    except Exception as e:
        flash(f"Error for Done Option:{str(e)}", "error")
    return redirect("/")

@app.route("/done/<int:taskno>")
def done(taskno):
    try:
        MarkDone(taskno)
    except Exception as e:
        flash(f"Error for Delete Option:{str(e)}", "error")
    return redirect("/")

@app.route("/update/<int:taskno>", methods=["POST", "GET"])
def update(taskno):
    if request.method == "POST":
        newtask = request.form.get("task")
        if request.form.get("cattext") and request.form.get("catdrop"):
            flash(f"Error! Please add a new task or select from a previous task", "error") 
            return redirect(f"/update/{taskno}") 
        else:
            newcat = request.form.get("cattext") or request.form.get("catdrop")
            try:
                UpdateTask(taskno, newtask, newcat)
            except Exception as e:
                flash(f"Error for Update Option:{str(e)}", "error")
            return redirect("/")
    else:
        with get_db() as con:
            cur = con.cursor()
            cur.execute("SELECT task, category FROM tasks where id = ?", (taskno,))
            (task, category) = cur.fetchone()
            cur.execute("SELECT DISTINCT category FROM tasks")
            categories = cur.fetchall()
    return render_template("update.html", taskno=taskno, task=task, category = category, categories = categories)

init_table()

if __name__=="__main__":
    app.run(debug=True)