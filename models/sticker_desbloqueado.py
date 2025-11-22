from utils.db import db
from models.sticker import Sticker

class StickerDesbloqueado(db.Model):
    __tablename__ = 'sticker_desbloqueado'

    # Características
    id_usuario = db.Column(
        db.Integer,
        primary_key=True,
        nullable=True
    )

    id_sticker = db.Column(
        db.Integer,
        db.ForeignKey('sticker.id_sticker'),
        primary_key=True,
        nullable=True
    )


    # Relaciones
    sticker = db.relationship(
        'Sticker',
        backref='stickerdesbloqueado_sticker'
    )


    # Objeto
    def __init__(self,
                 id_usuario,
                 id_sticker):
        self.id_usuario = id_usuario
        self.id_sticker = id_sticker