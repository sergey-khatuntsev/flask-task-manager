from flask_restx import Api, Namespace, Resource, fields
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth.models import User

api_bp = Blueprint('api', __name__, url_prefix='/api')

api = Api(
    api_bp,
    version='1.0',
    title='Project API',
    description='API Documentation for the Project',
    doc='/docs' 
)

# ---------------------------
# TASKS Namespace
# ---------------------------
tasks_ns = Namespace('tasks', description='Task management API')

task_model = tasks_ns.model('Task', {
    'id': fields.Integer(readOnly=True, description='Unique identifier'),
    'title': fields.String(required=True, description='Title of the task'),
    'description': fields.String(description='Description of the task'),
    'done': fields.Boolean(default=False, description='Completion status'),
})

task_create_model = tasks_ns.model('TaskCreate', {
    'title': fields.String(required=True, description='Title of the task'),
    'description': fields.String(description='Description of the task'),
})

@tasks_ns.route('/')
class TaskList(Resource):
    @tasks_ns.marshal_list_with(task_model)
    @login_required
    def get(self):
        """Get all tasks"""
        from app.tasks.models import Task
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return tasks

    @tasks_ns.expect(task_create_model)
    @tasks_ns.marshal_with(task_model, code=201)
    @login_required
    def post(self):
        """Create a new task"""
        from app.tasks.models import Task 
        data = request.json
        if not data.get('title'):
            tasks_ns.abort(400, "Title is required.")
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        return new_task, 201

@tasks_ns.route('/<int:task_id>')
class TaskResource(Resource):
    @tasks_ns.marshal_with(task_model)
    @login_required
    def get(self, task_id):
        """Get task by ID"""
        from app.tasks.models import Task 
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            tasks_ns.abort(404, "Task not found.")
        return task

    @tasks_ns.expect(task_model)
    @tasks_ns.marshal_with(task_model)
    @login_required
    def put(self, task_id):
        """Update task by ID"""
        from app.tasks.models import Task 
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            tasks_ns.abort(404, "Task not found.")
        data = request.json
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.done = data.get('done', task.done)
        db.session.commit()
        return task

    @tasks_ns.response(204, 'Task deleted')
    @login_required
    def delete(self, task_id):
        """Delete task by ID"""
        from app.tasks.models import Task 
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            tasks_ns.abort(404, "Task not found.")
        db.session.delete(task)
        db.session.commit()
        return '', 204

api.add_namespace(tasks_ns, path='/tasks')

# ---------------------------
# AUTH Namespace
# ---------------------------
auth_ns = Namespace('auth', description='Authentication API')

user_model = auth_ns.model('User', {
    'username': fields.String(required=True, description='The username'),
    'email': fields.String(required=True, description='The email address'),
    'password': fields.String(required=True, description='The password'),
})

login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The password'),
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        """Register a new user"""
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            return {"message": "User already exists"}, 400
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'] 
        )
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User registered successfully"}, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        """Login a user"""
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']: 
            login_user(user)
            return {"message": "Login successful"}, 200
        return {"message": "Invalid username or password"}, 401

@auth_ns.route('/logout')
class Logout(Resource):
    def post(self):
        """Logout the current user"""
        logout_user()
        return {"message": "Logout successful"}, 200

api.add_namespace(auth_ns, path='/auth')
