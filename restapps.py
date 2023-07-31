from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api 
from datetime import datetime
import json


app = Flask(__name__)
api = Api(app)


# setting up database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.sqlite3"
db = SQLAlchemy()
db.init_app(app)


#Model
class Task(db.Model):
    task_no = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    due_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.String, default = "To Do", nullable=False)
    # task_priority = db.Column(db.Integer,)
    def __repr__(self):
        return "  |  ".join([self.name,"Due date : ", str(self.due_date),
        "Created date : ", str(self.created_date),"Status : ",self.status])+"\n"
        
    def to_dict(self):
        return json.dumps({"Task No. ": self.task_no,"Task Name : ":self.name,"Due date": str(self.due_date),
        "Created date " : str(self.created_date),"Status ":self.status}
        ,default=str,sort_keys=True)


## To create a new database
with app.app_context():
    db.create_all()

### VIEWS ---------------------------------------------------------------------------

## To get 
class GetTask(Resource):
    def get(self):
        tasks_list = Task.query.all()
        tasks_list = [task.to_dict() for task in tasks_list]
        return {"Tasks": tasks_list}
    

api.add_resource(GetTask, "/")


## To add 
class PostTask(Resource):
    def post(self):
        if request.is_json:
            task = Task(task = request.json["Task"],
                        due_date = datetime.strptime(request.json["Due date"],"%Y-%m-%d"),
                        status = request.json["Status"])
            db.session.add(task)
            db.session.commit()
            return {"Message": "Task created successfully","data":task.to_dict()},201
        else:
            return {"Error ": "request must be a JSON object"}

api.add_resource(PostTask,"/add")

## To edit
class PutTask(Resource):
    def get(self,no):
        task = Task.query.get_or_404(no)
        return task.to_dict()
    
    def put(self,no):
        if request.is_json:
            task = self.get(no)
            if task:
                task.name = request.json["Task"]
                task.due_date = datetime.fromisocformat(request.json["due_date"])
                db.session.commit()
                return {"Message": "Task edited successfully","data":task.to_dict()},201
        else:
            return {"Error": "Invalid JSON object"}
            
api.add_resource(PutTask,"/edit/<int:no>")

class DeleteTask(Resource):
    def get(self,no):
        task = Task.query.get_or_404(no)
        return task.to_dict()
    
    def delete(self, no):
        if request.is_json:
            task_to_be_deleted = self.get(no)
            Task.query.filter_by(no).delete()


app.run(debug=True)

# @app.route("")