from utils.db import db

class Sticker(db.Model):
    __tablename__ = 'sticker'

    # Características
    id_sticker = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=True
    )

    url_imagen = db.Column(
        db.Text,
        nullable=True
    )

    precio = db.Column(
        db.Integer,
        nullable=True
    )

    categoria = db.Column(
        db.Integer,
        nullable=True
    )


    # Objeto
    def __init__(self,
                 url_imagen,
                 precio,
                 categoria):
        self.url_imagen = url_imagen
        self.precio = precio
        self.categoria = categoria