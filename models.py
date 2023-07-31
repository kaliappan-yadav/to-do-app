from app import db
from flask_login import UserMixin
from datetime import datetime

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

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username
