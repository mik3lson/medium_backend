from extensions import db
from datetime import datetime
import json

class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    image = db.Column(db.Text)
    tags = db.Column(db.JSON)
    claps = db.Column(db.Integer, default=0)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    replies = db.relationship("Reply", backref="post", lazy=True, cascade="all, delete")
