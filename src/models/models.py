from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    board = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Post {self.id}>'
    
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', backref='prediction')

    def __repr__(self):
        return f'<Predictions {self.id}>'
    