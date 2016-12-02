from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy

# Flask-Login
login_manager = LoginManager()

# Flask-SQLAlchemy extension instance
db = SQLAlchemy()