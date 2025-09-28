from utils.db import db

class Insignia(db.Model):
    __tablename__ = 'insignia'

    # Características
    id_insignia = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=True
    )

    nombre = db.Column(
        db.String(25),
        unique=True,
        nullable=True
    )

    url_imagen = db.Column(
        db.Text,
        nullable=True
    )

    ptos_necesarios = db.Column(
        db.Integer,
        nullable=True
    )

    nivel = db.Column(
        db.Integer,
        nullable=True
    )

    tipo_ptos = db.Column(
        db.Integer,
        nullable=True
    )


    # Objeto
    def __init__(self,
                 nombre,
                 url_imagen,
                 ptos_necesarios,
                 nivel,
                 tipo_ptos):
        self.nombre = nombre
        self.url_imagen = url_imagen
        self.ptos_necesarios = ptos_necesarios
        self.nivel = nivel
        self.tipo_ptos = tipo_ptos