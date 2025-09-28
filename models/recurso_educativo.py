from utils.db import db

class RecursoEducativo(db.Model):
    __tablename__ = 'recurso_educativo'

    # Características
    id_recurso = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=True
    )

    titulo = db.Column(
        db.String(45),
        unique=True,
        nullable=True
    )

    autor = db.Column(
        db.String(20),
        nullable=True
    )

    fuente_url = db.Column(
        db.Text,
        nullable=True
    )

    tipo = db.Column(
        db.Integer,
        nullable=True
    )

    img_portada = db.Column(
        db.Text,
        nullable=True
    )

    
    # Objeto
    def __init__(self,
                 titulo,
                 autor,
                 fuente_url,
                 tipo,
                 img_portada):
        self.titulo = titulo
        self.autor = autor
        self.fuente_url = fuente_url
        self.tipo = tipo
        self.img_portada = img_portada