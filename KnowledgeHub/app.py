# tutorial: https://www.digitalocean.com/community/tutorials/how-to-perform-flask-sqlalchemy-migrations-using-flask-migrate
import os

from flask import Flask, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()
def get_env_variable(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise RuntimeError(f"Error: The environment variable {var_name} is not set.")
    return value


db = SQLAlchemy()
# to populate data refer to this:
## https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application
def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
    app.config["SECRET_KEY"] = get_env_variable("FLASK_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = get_env_variable("FLASK_SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_ECHO"] = get_env_variable("FLASK_SQLALCHEMY_ECHO").lower() == "true"
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/db_courses'
    # Define and ensure "uploads" folder exists
    upload_folder = os.path.join(app.static_folder, 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder


    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    # login_manager.login_view = "login"  # Redirect to login page if not logged in
    # login_manager.login_message = "Please log in to access this page."
    # login_manager.login_message_category = "warning"
    
    from models import User
    
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    
    @login_manager.unauthorized_handler
    def unauthorize_callback():
        return redirect(url_for('login'))

    bcrypt = Bcrypt(app)

    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        access_token_url='https://accounts.google.com/o/oauth2/token',
        access_token_params = None,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        authorize_params=None,
        api_base_url='https://www.googleapis.com/oauth2/v1/',
        userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={'scope': 'openid email profile'},
        jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
    )

    
    github = oauth.register(
        name='github',
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com',
        client_kwargs={'scope': 'user:email'}

    )

    from routes import register_routes
    register_routes(app, db, bcrypt,oauth)

    migrate = Migrate(app, db)

    return app

