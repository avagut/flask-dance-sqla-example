"""Contain the user authentication data structures."""

from app_folder import db
from flask_login import UserMixin
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


class User(UserMixin, db.Model):
    """Contain the user details."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    # ... other columns as needed


class OAuth(db.Model, OAuthConsumerMixin):
    """Contain the associated Oauth."""

    provider_user_id = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
