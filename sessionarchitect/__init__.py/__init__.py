from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# 1. Initialize our main tools (like global variables)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Where to redirect if user isn't logged in

# 2. Function to create and configure the app
def create_app():
    app = Flask(__name__)
    
    # 3. CONFIGURE SECURITY & DATABASE (CRITICAL!)
    # **********************************************
    # NOTE: YOU MUST ADD YOUR OWN SECRET_KEY IN YOUR .env FILE
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-dev-key') 
    
    # Replace this with your PostgreSQL connection string for production.
    # For now, we'll use a simple local SQLite file to get running quickly.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 4. Connect tools to the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # 5. Import and register the different "rooms" (Blueprints)
    from sessionarchitect.auth.routes import auth
    from sessionarchitect.generator.routes import generator
    app.register_blueprint(auth)
    app.register_blueprint(generator)
    
    return app