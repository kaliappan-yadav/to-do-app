from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    request,
    session
)

from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from app import create_app,db,login_manager,bcrypt
from datetime import datetime
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
)

from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp ,Optional
from flask_login import current_user
from wtforms import ValidationError,validators
from forms import login_form,register_form
from datetime import timedelta
from models import User, Task

# url_for("static")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
app = create_app()


@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html",title="Home")


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():

    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )



# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))
        
        except:
            return redirect(url_for('register'))

@app.route("/home/<string:role>")
@login_required
def home(role):
    if role is None:
        return redirect("/login")
    print(role)
    tasks = Task.query.all()
    if role=='user':
        return render_template("employee.html",tasks=tasks)
    return render_template("index.html",tasks = tasks)


@app.route("/add/", methods=["GET","POST"])
@login_required
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
@login_required
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
@login_required
def delete_task(no):
    db.session.query(Task).filter(Task.task_no == no).delete()
    # task = Task.query.delete(no)
    db.session.commit()
    return redirect("/")
    # return render_template("delete_task.html",task)


@app.route("/complete/<int:no>")
@login_required
def mark_task_complete(no):
    task = Task.query.get(no)
    task.status = "Completed"
    db.session.commit()
    return redirect("/")

@login_required
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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("login")