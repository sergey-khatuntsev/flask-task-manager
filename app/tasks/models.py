from .. import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    done = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="active")  # New field for task status
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.title} - {self.status}>'

