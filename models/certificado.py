from utils.db import db
from sqlalchemy.dialects.postgresql import JSONB

class Certificado(db.Model):
    __tablename__ = 'certificado'

    # Características
    id_certificado = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=True
    )

    nombre = db.Column(
        db.String(20),
        unique=True,
        nullable=True
    )

    url_imagen = db.Column(
        db.Text,
        nullable=True
    )

    requisito_1 = db.Column(
        db.Integer,
        db.ForeignKey('insignia.id_insignia'),
        nullable=True
    )

    requisito_2 = db.Column(
        db.Integer,
        db.ForeignKey('insignia.id_insignia'),
        nullable=True
    )

    requisito_3 = db.Column(
        db.Integer,
        db.ForeignKey('insignia.id_insignia'),
        nullable=True
    )

    plantilla = db.Column(
        JSONB,
        nullable=True
    )

    nivel = db.Column(
        db.Integer,
        nullable=True
    )


    # Relaciones
    req_insignia_1 = db.relationship(
        'Insignia',
        foreign_keys=[requisito_1],
        backref='certificado_requisito_1'
    )

    req_insignia_2 = db.relationship(
        'Insignia',
        foreign_keys=[requisito_2],
        backref='certificado_requisito_2'
    )

    req_insignia_3 = db.relationship(
        'Insignia',
        foreign_keys=[requisito_3],
        backref='certificado_requisito_3'
    )

    # Objeto
    def __init__(self,
                 nombre,
                 url_imagen,
                 requisito_1,
                 requisito_2,
                 requisito_3,
                 plantilla,
                 nivel):
        self.nombre = nombre
        self.url_imagen = url_imagen
        self.requisito_1 = requisito_1
        self.requisito_2 = requisito_2
        self.requisito_3 = requisito_3
        self.plantilla = plantilla
        self.nivel = nivel