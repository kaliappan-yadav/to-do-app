from flask import Flask,render_template,redirect,request,render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
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
    
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')
# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
# Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)
# Create all database tables
db.create_all()
# Create 'member@example.com' user with no roles
if not User.query.filter(User.email == 'member@example.com').first():
    user = User(
        email='member@example.com',
        email_confirmed_at=datetime.datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    db.session.add(user)
    db.session.commit()
# Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.email == 'admin@example.com').first():
    user = User(
        email='admin@example.com',
        email_confirmed_at=datetime.datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()

@app.route('/')
def home_page():
    return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>{%trans%}Home page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('home_page') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                <p><a href={{ url_for('admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """)
@app.route('/members')
@login_required    # Use of @login_required decorator
def member_page():
    return render_template_string("""
            {% extends "flask_user_layout.html" %}
            {% block content %}
                <h2>{%trans%}Members page{%endtrans%}</h2>
                <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                <p><a href={{ url_for('home_page') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                <p><a href={{ url_for('member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                <p><a href={{ url_for('admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
            {% endblock %}
            """)
# The Admin page requires an 'Admin' role.
@app.route('/admin')
@roles_required('Admin')    # Use of @roles_required decorator
def admin_page():
        return render_template_string("""
                {% extends "flask_user_layout.html" %}
                {% block content %}
                    <h2>{%trans%}Admin Page{%endtrans%}</h2>
                    <p><a href={{ url_for('user.register') }}>{%trans%}Register{%endtrans%}</a></p>
                    <p><a href={{ url_for('user.login') }}>{%trans%}Sign in{%endtrans%}</a></p>
                    <p><a href={{ url_for('home_page') }}>{%trans%}Home Page{%endtrans%}</a> (accessible to anyone)</p>
                    <p><a href={{ url_for('member_page') }}>{%trans%}Member Page{%endtrans%}</a> (login_required: member@example.com / Password1)</p>
                    <p><a href={{ url_for('admin_page') }}>{%trans%}Admin Page{%endtrans%}</a> (role_required: admin@example.com / Password1')</p>
                    <p><a href={{ url_for('user.logout') }}>{%trans%}Sign out{%endtrans%}</a></p>
                {% endblock %}
                """)


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

@app.route('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect("/")
    return render_template('login.html', error=error)