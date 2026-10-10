from flask import Flask, render_template, request, redirect
from models import db, Task, Subject, User
from datetime import date

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///studyplanner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            return redirect("/dashboard")

        return "Invalid username or password!"

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists!"

        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return f"Account created for {username}!"

    return render_template("register.html")


@app.route("/logout")
def logout():
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    tasks = Task.query.all()
    subjects = Subject.query.all()

    total_tasks = len(tasks)
    completed_tasks = len(
        [task for task in tasks if task.completed]
    )

    if total_tasks > 0:
        progress = int(
            (completed_tasks / total_tasks) * 100
        )
    else:
        progress = 0

    today = date.today()

    for task in tasks:
        try:
            deadline_date = date.fromisoformat(task.deadline)
            days_left = (deadline_date - today).days

            if days_left < 0:
                task.deadline_status = "Overdue"
            elif days_left == 0:
                task.deadline_status = "Due Today"
            elif days_left <= 3:
                task.deadline_status = "Due Soon"
            else:
                task.deadline_status = "Upcoming"

        except ValueError:
            task.deadline_status = ""

    return render_template(
        "dashboard.html",
        tasks=tasks,
        subjects=subjects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        progress=progress
    )


@app.route("/subject", methods=["GET", "POST"])
def subject():
    if request.method == "POST":
        subject_name = request.form["subject"]

        new_subject = Subject(
            subject_name=subject_name
        )

        db.session.add(new_subject)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("subject.html")


@app.route("/delete_subject/<int:subject_id>")
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)

    if subject:
        db.session.delete(subject)
        db.session.commit()

    return redirect("/dashboard")


@app.route("/task", methods=["GET", "POST"])
def task():
    subjects = Subject.query.all()

    if request.method == "POST":
        task_name = request.form["task"]
        subject_name = request.form["subject"]
        deadline = request.form["deadline"]
        priority = request.form["priority"]

        new_task = Task(
            task_name=task_name,
            subject=subject_name,
            deadline=deadline,
            priority=priority
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect("/dashboard")

    return render_template(
        "task.html",
        subjects=subjects
    )


@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    task = Task.query.get(task_id)

    if task:
        task.completed = True
        db.session.commit()

    return redirect("/dashboard")


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get(task_id)

    if task:
        db.session.delete(task)
        db.session.commit()

    return redirect("/dashboard")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)