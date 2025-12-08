from flask_restful import Resource, reqparse
from flask import request
from helpers.database import db
from models.cbo_model import TableCBO


def cbo_to_dict(cbo: TableCBO):
    return {
        "codigo": cbo.codigo,
        "titulo": cbo.titulo,
        "created_at": cbo.created_at,
        "updated_at": cbo.updated_at,
    }

parser = reqparse.RequestParser()
parser.add_argument("titulo", type=str, required=True, help="O campo 'titulo' é obrigatório")

class CBOListResource(Resource):
    # GET /cbo?page=1&per_page=20
    def get(self):
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        paginated = TableCBO.query.order_by(TableCBO.codigo).paginate(page=page, per_page=per_page)

        return {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "items": [cbo_to_dict(cbo) for cbo in paginated.items],
        }, 200

    # POST 
    def post(self):
        data = parser.parse_args()

        
        codigo = request.json.get("codigo")
        if not codigo:
            return {"message": "O campo 'codigo' é obrigatório"}, 400

        
        if TableCBO.query.get(codigo):
            return {"message": "Já existe um CBO com esse código"}, 400

        cbo = TableCBO(
            codigo=codigo,
            titulo=data["titulo"]
        )

        db.session.add(cbo)
        db.session.commit()

        return cbo_to_dict(cbo), 201


class CBODetailResource(Resource):
    # GET 
    def get(self, codigo):
        cbo = TableCBO.query.get(codigo)
        if not cbo:
            return {"message": "CBO não encontrado"}, 404

        return cbo_to_dict(cbo), 200

    # PUT 
    def put(self, codigo):
        data = parser.parse_args()

        cbo = TableCBO.query.get(codigo)
        if not cbo:
            return {"message": "CBO não encontrado"}, 404

        cbo.titulo = data["titulo"]

        db.session.commit()

        return cbo_to_dict(cbo), 200

    # DELETE 
    def delete(self, codigo):
        cbo = TableCBO.query.get(codigo)
        if not cbo:
            return {"message": "CBO não encontrado"}, 404

        db.session.delete(cbo)
        db.session.commit()

        return {"message": "CBO removido com sucesso"}, 200
