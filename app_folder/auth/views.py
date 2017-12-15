
from flask import Flask, redirect, url_for, flash, render_template, Blueprint
from flask_dance.contrib.github import make_github_blueprint, github
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized, oauth_error

from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)

from app_folder import app, db
from . import models

users_blueprint = Blueprint('auth', __name__, template_folder='templates')
github_blueprint = make_github_blueprint(
    client_id="61727a7e31e009cc3a39",
    client_secret="a8e28de3d4930fd9d62c3adcaf48560f414bee76",
)

# setup SQLAlchemy backend
github_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session, user=current_user)

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(github_blueprint, token):
    if not token:
        flash("Failed to log in with {name}".format(name=github_blueprint.name))
        return
    # figure out who the user is
    resp = github_blueprint.session.get("/user")
    if resp.ok:
        username = resp.json()["login"]
        query = models.User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            # create a user
            user = models.User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with GitHub")
    else:
        msg = "Failed to fetch user info from {name}".format(name=github_blueprint.name)
        flash(msg, category="error")

# notify on OAuth provider error
@oauth_error.connect_via(github_blueprint)
def github_error(github_blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=github_blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")

@users_blueprint.route('/rawlogin')
def rawlogin():
    user = models.User.query.filter_by(username='avagut').first()
    login_user(user)
    return 'You are now logged in!'

@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@users_blueprint.route('/home')
@login_required
def home():
    return 'The current user is ' + current_user.username 

@users_blueprint.route("/")
def login():
    return render_template("home.html")