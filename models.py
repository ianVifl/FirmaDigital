from app import db, login_manager
from flask_login import UserMixin
import datetime


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nombre_original = db.Column(db.String(255), nullable=False)
    nombre_sistema = db.Column(db.String(300), nullable=False, unique=True)
    hash_original = db.Column(db.String(64), nullable=False)
    fecha_subida = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    id_propietario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    propietario = db.relationship('Usuario', backref='documentos_subidos', foreign_keys=[id_propietario])


class Firma(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_documento = db.Column(db.Integer, db.ForeignKey('documento.id'), nullable=False)
    id_firmante = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')
    fecha_firma = db.Column(db.DateTime, nullable=True)
    documento = db.relationship('Documento', backref='firmas', foreign_keys=[id_documento])
    firmante = db.relationship('Usuario', backref='firmas_pendientes', foreign_keys=[id_firmante])