from app.models import db, Users
from flask import Flask
from config import Config
# from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app,db)
cors = CORS()
cors.init_app(app)

from . import routes
from . import models