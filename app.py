from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
# from flask_sqlalchemy.model import 
from datetime import datetime
app = Flask(__name__)

# setting up database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.sqlite3"
db = SQLAlchemy()
db.init_app(app)

# url_for("static")
#Model
class Task(db.Model):
    task_no = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String, nullable = False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String, default = "To Do", nullable=False)
    # task_priority = db.Column(db.Integer,)
    def __repr__(self):
        return "  |  ".join([self.task,"Due date : ", str(self.due_date),
        "Created date : ", str(self.created_date),"Status : ",self.status])+"\n"
        

with app.app_context():
    db.create_all()

@app.route("/")
def list_tasks():
    tasks = Task.query.all()
    return render_template("index.html",tasks = tasks)


@app.route("/add/", methods=["GET","POST"])
def create_task():
    if request.method == "POST":
        task = Task(task = request.form["task_name"],
                    due_date = datetime.strptime(request.form["due_date"],"%Y-%m-%d"),
                    status = request.form["status"])
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    return render_template("add_task.html")

@app.route("/edit/<int:no>",methods=["GET","POST"])
def edit_task(no):
    task_tobe_edited = Task.query.get(no)
    print(task_tobe_edited)
    if request.method == "POST":
        task_tobe_edited.task = request.form["task"]
        task_tobe_edited.status = request.form["status"]
        task_tobe_edited.due_date = datetime.fromisoformat(request.form["due_date"])
        db.session.commit()
        return redirect("/")
    return render_template("edit_task.html",task = task_tobe_edited)

@app.route("/delete/<int:no>")
def delete_task(no):
    db.session.query(Task).filter(Task.task_no == no).delete()
    # task = Task.query.delete(no)
    db.session.commit()
    return redirect("/")
    # return render_template("delete_task.html",task)


@app.route("/complete/<int:no>")
def mark_task_complete(no):
    task = Task.query.get(no)
    task.status = "Completed"
    db.session.commit()
    return redirect("/")

@app.route("/show/<int:no>")
def filter_task(no):
    print(no,type(no))
    if no:
        status_value = {1: "Completed", 2:"In Progress"}[no]
        print(status_value)
        tasks = Task.query.filter_by(status=status_value)
        # print(tasks)
        return render_template("index.html",tasks= tasks)
    return redirect("/")
# app.run(debug=True)
