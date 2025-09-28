from utils.db import db

class InsigniaDesbloqueada(db.Model):
    __tablename__ = 'insignia_desbloqueada'

    # Características
    id_usuario = db.Column(
        db.Integer,
        primary_key=True,
        nullable=True
    )

    id_insignia = db.Column(
        db.Integer,
        db.ForeignKey('insignia.id_insignia'),
        primary_key=True,
        nullable=True
    )


    # Relaciones
    insignia = db.relationship(
        'Insignia',
        backref='insigniadesbloqueada_insignia'
    )


    # Objeto
    def __init__(self,
                 id_usuario,
                 id_insignia):
        self.id_usuario = id_usuario
        self.id_insignia = id_insignia