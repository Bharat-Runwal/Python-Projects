from flask import Flask
from config import Config
from flask_sqlachemy import SQLAlchemy
app = Flask(__name__)
app.config.from_object(Config)
db=
from app import routes
