"""Project Initialize."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('flask.cfg', silent=True)


db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

from app_folder.auth.models import User


@login_manager.user_loader
def load_user(user_id):
    """Fetch the associated user from given user_id."""
    return User.query.get(int(user_id))


from app_folder.auth.views import users_blueprint
from app_folder.auth.views import github_blueprint
from app_folder.auth.views import google_blueprint
from app_folder.auth.views import twitter_blueprint

# register the blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(github_blueprint, url_prefix="/login")
app.register_blueprint(google_blueprint, url_prefix="/login")
app.register_blueprint(twitter_blueprint, url_prefix='/twitter_login')
