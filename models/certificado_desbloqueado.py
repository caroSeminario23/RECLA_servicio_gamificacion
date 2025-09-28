from utils.db import db

class CertificadoDesbloqueado(db.Model):
    __tablename__ = 'certificado_desbloqueado'

    # Características
    id_usuario = db.Column(
        db.Integer,
        primary_key=True,
        nullable=True
    )

    id_certificado = db.Column(
        db.Integer,
        db.ForeignKey('certificado.id_certificado'),
        primary_key=True,
        nullable=True
    )

    insignia_1 = db.Column(
        db.Boolean,
        nullable=True
    )

    insignia_2 = db.Column(
        db.Boolean,
        nullable=True
    )

    insignia_3 = db.Column(
        db.Boolean,
        nullable=True
    )

    desbloqueado = db.Column(
        db.Boolean,
        nullable=True
    )


    # Objeto
    def __init__(self,
                 id_usuario,
                 id_certificado):
        self.id_usuario = id_usuario
        self.id_certificado = id_certificado