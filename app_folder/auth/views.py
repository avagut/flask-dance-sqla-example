"""User Auth Routes using Flask Dance."""

from flask import redirect, url_for, flash, render_template, Blueprint
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.contrib.facebook import make_facebook_blueprint
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
    api_key=app.config.get('TWITTER_API_KEY'),
    api_secret=app.config.get('TWITTER_API_SECRET')
)

facebook_blueprint = make_facebook_blueprint(
    client_id=app.config.get('FACEBOOK_APP_ID'),
    client_secret=app.config.get('FACEBOOK_APP_SECRET')
)

# setup SQLAlchemy backend
github_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session,
                                             user=current_user)
google_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session,
                                             user=current_user)
twitter_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session,
                                              user=current_user, user_required=False)
facebook_blueprint.backend = SQLAlchemyBackend(models.OAuth, db.session,
                                               user=current_user)


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    """Log in user on successful Github authorization."""
    if not token:
        flash("Failed to log in with GitHub.", category="error")
        return False
    resp = blueprint.session.get("/user")
    if not resp.ok:
        msg = "Failed to fetch user info from GitHub."
        flash(msg, category="error")
        return False
    github_info = resp.json()
    github_user_id = str(github_info["id"])
# Find this OAuth token in the database, or create it
    query = models.OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=github_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = models.OAuth(
            provider=blueprint.name,
            provider_user_id=github_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with GitHub.")

    else:
        # Create a new local user account for this user
        username = github_info["login"]
        user = models.User(username=username)
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with GitHub.")
    # Disable Flask-Dance's default behavior for saving the OAuth token
    # return False
    return redirect(url_for("auth.home"))


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
    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info from GitHub."
        flash(msg, category="error")
        return False

    user_info = resp.json()
    user_id = str(user_info["id"])
# Find this OAuth token in the database, or create it
    query = models.OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = models.OAuth(
            provider=blueprint.name,
            provider_user_id=user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with Google.")

    else:
        # Create a new local user account for this user
        username = user_info["email"]
        user = models.User(username=username)
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with Google.")
    # Disable Flask-Dance's default behavior for saving the OAuth token
    # return False
    return redirect(url_for("auth.home"))


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
    resp = blueprint.session.get('account/settings.json')
    if not resp.ok:
        msg = "Failed to fetch user info from Twitter."
        flash(msg, category="error")
        return False
    user_info = resp.json()
    print(type(token))
    user_id = str(token["user_id"])
# Find this OAuth token in the database, or create it
    query = models.OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = models.OAuth(
            provider=blueprint.name,
            provider_user_id=user_id,
            token=token,
        )
    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with Twitter.")

    else:
        # Create a new local user account for this user
        username = user_info["screen_name"]
        user = models.User(username=username)
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with Twitter.")
    # Disable Flask-Dance's default behavior for saving the OAuth token
    # return False
    return redirect(url_for("auth.home"))


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


# create/login local user on successful OAuth login
@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint, token):
    """Log in user on successful Github authorization."""
    if not token:
        flash("Failed to log in {name}".format(name=blueprint.name))
        return
    # figure out who the user is
    resp = blueprint.session.get("/me")
    if resp.ok:
        username = resp.json()["name"]
        query = models.User.query.filter_by(username=username)
        try:
            user = query.one()
        except NoResultFound:
            # create a user
            user = models.User(username=username)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash("Successfully signed in with Facebook")
    else:
        msg = "Failed to fetch user info from {name}".format(
              name=blueprint.name)
        flash(msg, category="error")
    return redirect(url_for("auth.home"))


# notify on OAuth provider error
@oauth_error.connect_via(facebook_blueprint)
def facebook_error(blueprint, error, error_description=None, error_uri=None):
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
    return render_template("logged_in.html")


@users_blueprint.route("/")
def login():
    """Create default route for unauthenticated redirect."""
    return render_template("login.html")
