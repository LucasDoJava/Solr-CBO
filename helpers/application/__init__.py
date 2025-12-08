from flask import Flask
from flask_restful import Api

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:123456@localhost:5432/habits"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

api = Api(app)
