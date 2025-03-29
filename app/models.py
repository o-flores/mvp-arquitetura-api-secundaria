from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ValidationCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document = db.Column(db.String(18), unique=True, nullable=False)
    is_valid = db.Column(db.Boolean, nullable=False)
    doc_type = db.Column(db.String(4), nullable=False)

    def __repr__(self):
        return f'<ValidationCache {self.document}>'