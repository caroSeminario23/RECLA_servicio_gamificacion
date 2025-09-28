from utils.db import db

class HistoriaNotas(db.Model):
    __tablename__ = 'historia_notas'

    # Características
    id_recurso = db.Column(
        db.Integer,
        primary_key=True,
        nullable=True
    )

    id_usuario = db.Column(
        db.Integer,
        primary_key=True,
        nullable=True
    )

    fec_estudiado = db.Column(
        db.DateTime,
        primary_key=True,
        nullable=True
    )

    nota_anterior = db.Column(
        db.Integer,
        nullable=True
    )


    # Objeto
    def __init__(self,
                 id_recurso,
                 id_usuario,
                 nota_anterior):
        self.id_recurso = id_recurso
        self.id_usuario = id_usuario
        self.nota_anterior = nota_anterior