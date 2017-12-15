from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
 
 
from app_folder.auth.models import User
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from app_folder.auth.views import users_blueprint
from app_folder.auth.views import github_blueprint
 
# register the blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(github_blueprint, url_prefix="/login")
