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
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required, UserMixin
from datetime import datetime
from forms import register_form, login_form
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
) 

app = Flask(__name__)
app.secret_key = "secret-key"
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)
bcrypt = Bcrypt()
bcrypt.init_app(app)
# setting up database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.sqlite3"
db = SQLAlchemy()
db.init_app(app)

# url_for("static")
#Model

  
    
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    # User information
    user_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    role = db.Column(db.String(10))

    def __repr__(self):
        return self.user_name




class Task(db.Model):
    task_no = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String, nullable = False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String, default = "To Do", nullable=False)
    assignee_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    assigner_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')
    )
    # task_priority = db.Column(db.Integer,)
    def __repr__(self):
        return "  |  ".join([self.task,"Due date : ", str(self.due_date),
        "Created date : ", str(self.created_date),"Status : ",self.status])+"\n"
  
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/")
def view_tasks():
    if not current_user.is_authenticated:
        return redirect("/login")
    tasks = Task.query.filter_by(assignee_id=current_user.id)
    if current_user.role == "Manager":
        tasks = tasks.union(Task.query.filter_by(assigner_id=current_user.id))
    # tasks = Task.query.filter_by(assignee_id=current_user.id)
    users = User.query.all()
    user_id_name_map = {}
    for user in users:
        user_id_name_map[user.id] = user.user_name
        
    return render_template("view_task.html",tasks = tasks,user=user_id_name_map)


@app.route("/login/", methods=["GET", "POST"], strict_slashes=False)
def login():
    if request.method=="POST":
        user_name = request.form['username']
        passwd = request.form['password']
        user = User.query.filter_by(user_name=user_name).first()

        if user and user.password==passwd:
            login_user(user)
            return redirect(url_for('view_tasks'))
        else:
            flash("Invalid Username or password!", "danger")
            return render_template("registration.html")
    return render_template("login.html")
    # form = login_form()

    # if form.validate_on_submit():
    #     try:
    #         user = User.query.filter_by(email=form.email.data).first()
    #         if check_password_hash(user.pwd, form.pwd.data):
    #             login_user(user)
    #             return redirect(url_for('index'))
    #         else:
    #             flash("Invalid Username or password!", "danger")
    #     except Exception as e:
    #         flash(e, "danger")

    # return render_template("auth.html",
    #     form=form,
    #     text="Login",
    #     title="Login",
    #     btn_action="Login"
    #     )



# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    if request.method=="POST":
        user_name = request.form["username"]
        passwd = request.form["password"]
        role = request.form["role"]
        # if not user_name or not passwd:
        #     return render_template(url_for("register"))
        newuser = User(
                user_name=user_name,
                password=passwd,
                role = role
            )
        db.session.add(newuser)
        db.session.commit()
        flash(f"Account Succesfully created", "success")
        return redirect(url_for("login"))
        
        
    return render_template("registration.html")
    # form = register_form()
    # if form.validate_on_submit():
    #     try:
    #         email = form.email.data
    #         pwd = form.pwd.data
    #         username = form.username.data
            
    #         newuser = User(
    #             username=username,
    #             email=email,
    #             pwd=bcrypt.generate_password_hash(pwd),
    #         )
    
    #         db.session.add(newuser)
    #         db.session.commit()
    #         flash(f"Account Succesfully created", "success")
    #         return redirect(url_for("login"))
        
    #     except:
    #         return redirect(url_for('register'))

@app.route("/add/", methods=["GET","POST"])
def create_task():
    if current_user.role!="Manager":
        flash("Only Manager can add new tasks","danger")
        return render_template("view_task.html")
    if request.method == "POST":
        task = Task(task = request.form["task_name"],
                    due_date = datetime.strptime(request.form["due_date"],"%Y-%m-%d"),
                    status = request.form["status"],
                    assignee_id=request.form["assignee_id"],
                    assigner_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    users = User.query.all()
    return render_template("add_task.html", assignees=users)

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
    if current_user.role!="Manager":
        return redirect("/")
    db.session.query(Task).filter(Task.task_no == no).delete()
    # task = Task.query.delete(no)
    db.session.commit()
    return redirect("/")
    # return render_template("delete_task.html",task)


@app.route("/complete/<int:no>")
def mark_task_complete(no):
    task = Task.query.get(task.no==no & task.assignee_id==)
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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# app.run(debug=True)
