"""User Auth Routes using Flask Dance."""

from flask import redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import (current_user, login_required, login_user, logout_user)
from app_folder import app, db
from . import models


users_blueprint = Blueprint('auth', __name__, template_folder='templates')
github_blueprint = make_github_blueprint(
    client_id=app.config.get('GITHUB_ID'),
    client_secret=app.config.get('GITHUB_SECRET'),
)
google_blueprint = make_google_blueprint(
    client_id=app.config.get('GOOGLE_ID'),
    client_secret=app.config.get('GOOGLE_SECRET'),
    scope=["profile", "email"]
)

twitter_blueprint = make_twitter_blueprint(
    api_key="4rBQP1r4iP2oPRFpHfRY5ofd1",
    api_secret="3Bdf5kVIlHUZSmQDWuuKT0DyiAaOreiAN95mRFqQ64JssiSgnH",
)


# setup SQLAlchemy backend
github_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session,
                                             user=current_user)
google_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session,
                                             user=current_user)
twitter_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session,
                                              user=current_user)


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    """Log in user on successful Github authorization."""
    if not token:
        flash("Failed to log in {name}".format(name=blueprint.name))
        return
    # figure out who the user is
    resp = blueprint.session.get("/user")
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
        msg = "Failed to fetch user info from {name}".format(
              name=blueprint.name)
        flash(msg, category="error")


# notify on OAuth provider error
@oauth_error.connect_via(github_blueprint)
def github_error(blueprint, error, error_description=None,
                 error_uri=None):
    """Throw error on authentication failure from Github."""
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    """Log in user on successful Google authorization."""
    if not token:
        flash("Failed to log in {name}".format(name=blueprint.name))
        return
    # figure out who the user is
    # resp = blueprint.session.get("/plus/v1/people/me")
    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if resp.ok:
        # print(resp.json())
        username = resp.json()["email"]
        query = models.User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            # create a user
            user = models.User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with Google")
    else:
        msg = "Failed to fetch user info from {name}".format(
              name=blueprint.name)
        flash(msg, category="error")


# notify on OAuth provider error
@oauth_error.connect_via(google_blueprint)
def google_error(blueprint, error, error_description=None,
                 error_uri=None):
    """Throw error on authentication failure from Google."""
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    """Log in user on successful Twitter authorization."""
    if not token:
        flash("Failed to log in {name}".format(name=blueprint.name))
        return
    # figure out who the user is
    # resp = blueprint.session.get("/plus/v1/people/me")
    resp = blueprint.session.get('account/settings.json')
    if resp.ok:
        # print(resp.json())
        username = resp.json()['screen_name']
        query = models.User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            # create a user
            user = models.User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with Twitter")
    else:
        msg = "Failed to fetch user info from {name}".format(
              name=blueprint.name)
        flash(msg, category="error")


# notify on OAuth provider error
@oauth_error.connect_via(twitter_blueprint)
def twitter_error(blueprint, error, error_description=None,
                  error_uri=None):
    """Throw error on authentication failure from Twitter."""
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")


@users_blueprint.route('/logout')
@login_required
def logout():
    """Log out current user."""
    logout_user()
    return redirect(url_for("auth.login"))


@users_blueprint.route('/home')
@login_required
def home():
    """Test page for fully authenticated user."""
    return 'The current user is ' + current_user.username


@users_blueprint.route("/")
def login():
    """Create default route for unauthenticated redirect."""
    return render_template("home.html")


@users_blueprint.route('/twitter')
def twitter_login():
    if not twitter.authorized:
        return redirect(url_for('twitter.login'))

    account_info = twitter.get('account/settings.json')
    account_info_json = account_info.json()

    return '<h1>Your Twitter name is @{}'.format(account_info_json['screen_name'])
