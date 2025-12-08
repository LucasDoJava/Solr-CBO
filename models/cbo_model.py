from helpers.database import db
from datetime import datetime


class TableCBO(db.Model):
    __tablename__ = "table_cbo"

    codigo = db.Column(db.String(50), primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<CBO {self.codigo} - {self.titulo}>"
