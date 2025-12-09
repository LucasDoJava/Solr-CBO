from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()



#flask db init
#flask db migrate -m "mensagem"
#flask db upgrade
