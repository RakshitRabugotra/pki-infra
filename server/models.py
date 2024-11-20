from sqlalchemy import inspect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from uuid import uuid4
import datetime

db = SQLAlchemy()


def get_uuid():
    return uuid4().hex


def now():
    return datetime.datetime.now()


# Models
class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    public_key = db.Column(db.String(700), nullable=False)  # Store public key as string
    is_verified = db.Column(
        db.Boolean, default=False
    )  # Boolean flag to indicate verification status
    sessions = db.relationship("Session", backref="user", lazy=True)

    @staticmethod
    def serialize(instance):
        return {
            "id": instance.id,
            "full_name": instance.full_name,
            "email": instance.email,
            "public_key": instance.public_key,
            "is_verified": instance.is_verified,
        }


class Session(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=now)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=get_uuid)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=now)
