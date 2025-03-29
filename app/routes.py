from flask import Flask, request, jsonify
from flask_openapi3 import OpenAPI, Info
from flask_cors import CORS
import logging
from app.models import db, ValidationCache  # Importe do models.py

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Crie a aplicação Flask e integre o OpenAPI
info = Info(title="mvp API", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mvp_database.db'  # Atualize para /app/data
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialize o SQLAlchemy com a aplicação
db.init_app(app)
CORS(app)

# Create tables on startup
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "API secundaria de validação de documentos está online!"}), 200

@app.route('/cache', methods=['POST'])
def add_to_cache():
    data = request.json
    logger.debug(f"Dados recebidos: {data}")
    document = data.get('document')
    is_valid = data.get('valid')
    doc_type = data.get('type')

    # Verifica se o documento já existe no cache
    existing = ValidationCache.query.filter_by(document=document).first()
    
    if existing:
        existing.is_valid = is_valid
        existing.doc_type = doc_type
        db.session.commit()
        return jsonify({"message": "Documento atualizado no cache"}), 200
    else:
        new_entry = ValidationCache(
            document=document,
            is_valid=is_valid,
            doc_type=doc_type
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Documento armazenado em cache"}), 201

@app.route('/cache', methods=['GET'])
def get_cache():

    documents = ValidationCache.query.all()
    logger.debug(f"Dados recebidos: {documents}")

    return jsonify([{
        "document": doc.document,
        "valid": doc.is_valid,
        "type": doc.doc_type,
    } for doc in documents]), 200

@app.route('/cache/<document>', methods=['GET'])
def get_document(document):
    logger.debug(f"Dados recebidos: {document}")

    doc = ValidationCache.query.filter_by(document=document).first()
    logger.debug(f"Dados recebidos: {doc}")
    if doc:
        return jsonify({
            "document": doc.document,
            "valid": doc.is_valid,
            "type": doc.doc_type
        }), 200
    else:
        return jsonify({"error": "Documento não encontrado no cache"}), 404

@app.route('/cache/<document>', methods=['PUT'])
def update_cache(document):
    doc = ValidationCache.query.filter_by(document=document).first()
    data = request.json
    doc.is_valid = data.get('valid', doc.is_valid)
    doc.doc_type = data.get('type', doc.doc_type)
    db.session.commit()
    return jsonify({"message": "Documento atualizado"}), 200

@app.route('/cache/<document>', methods=['DELETE'])
def delete_cache(document):
    logger.debug(f"document: {document}")

    doc = ValidationCache.query.filter_by(document=document).first()
    logger.debug(f"ValidationCache: {doc}")

    if not doc:
        return jsonify({"message": "Documento nao encontrado"}), 404
        
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"message": "Documento removido do cache"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Garante que o banco será criado
    app.run(host='0.0.0.0', port=8001, debug=True)
