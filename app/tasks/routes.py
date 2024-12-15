from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Task
from .. import db

tasks_bp = Blueprint('tasks', __name__, template_folder='templates/tasks')

@tasks_bp.route('/', methods=['GET', 'POST'])
@login_required
def tasks_page():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Task title is required!', 'danger')
        else:
            new_task = Task(title=title, description=description, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('tasks.tasks_page'))
    
    tasks = Task.query.filter_by(user_id=current_user.id, status="active").all()
    archived_tasks = Task.query.filter(Task.user_id == current_user.id, Task.status.in_(["archived", "deleted"])).all()
    return render_template('tasks/tasks.html', tasks=tasks, archived_tasks=archived_tasks)

@tasks_bp.route('/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        task.done = not task.done
        task.status = "archived" if task.done else "active"
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    else:
        flash('Task not found!', 'danger')
    return redirect(url_for('tasks.tasks_page'))

@tasks_bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task:
        task.status = "deleted"
        db.session.commit()
        flash('Task moved to archive as deleted!', 'success')
    else:
        flash('Task not found!', 'danger')
    return redirect(url_for('tasks.tasks_page'))

@tasks_bp.route('/reopen/<int:task_id>', methods=['POST'])
@login_required
def reopen_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task and task.status == "archived":
        task.status = "active"
        task.done = False
        db.session.commit()
        flash('Task reopened successfully!', 'success')
    else:
        flash('Task not found or not archived!', 'danger')
    return redirect(url_for('tasks.tasks_page'))

@tasks_bp.route('/full_delete/<int:task_id>', methods=['POST'])
@login_required
def full_delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if task and task.status == "deleted":
        db.session.delete(task)
        db.session.commit()
        flash('Task permanently deleted!', 'success')
    else:
        flash('Task not found or not marked as deleted!', 'danger')
    return redirect(url_for('tasks.tasks_page'))
