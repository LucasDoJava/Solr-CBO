from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from helpers.database import db
from resources.resource_cbo import CBOListResource, CBODetailResource
from resources.resource_cbo import CBOSearchResource

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:postgres@db:5432/CBO"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializa DB
    db.init_app(app)

    # Inicializa migrate
    Migrate(app, db)

    api = Api(app)

    # Rotas
    api.add_resource(CBOListResource, "/cbo")                    
    api.add_resource(CBODetailResource, "/cbo/<string:codigo>") 
    api.add_resource(CBOSearchResource, "/search") 

    return app
