from utils.db import db

class RERespuelto(db.Model):
    __tablename__ = 're_resuelto'

    # Características
    id_rec_edu = db.Column(
        db.Integer,
        db.ForeignKey('recurso_educativo.id_rec_edu'),
        primary_key=True,
        nullable=True
    )

    id_usuario = db.Column(
        db.Integer,
        primary_key=True,
        nullable=True
    )

    rpta1 = db.Column(
        db.String(16),
        nullable=True
    )

    rpta2 = db.Column(
        db.String(16),
        nullable=True
    )

    rpta3 = db.Column(
        db.String(16),
        nullable=True
    )

    rpta4 = db.Column(
        db.String(16),
        nullable=True
    )


    # Objeto
    def __init__(self,
                 id_rec_edu,
                 id_usuario,
                 rpta1,
                 rpta2,
                 rpta3,
                 rpta4):
        self.id_rec_edu = id_rec_edu
        self.id_usuario = id_usuario
        self.rpta1 = rpta1
        self.rpta2 = rpta2
        self.rpta3 = rpta3
        self.rpta4 = rpta4