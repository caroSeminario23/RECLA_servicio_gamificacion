from utils.db import db

class RecursoEducativo(db.Model):
    __tablename__ = 'recurso_educativo'

    # Características
    id_rec_edu = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=True
    )

    titulo = db.Column(
        db.String(50),
        unique=True,
        nullable=True
    )

    portada_url = db.Column(
        db.Text,
        nullable=True
    )

    referencia = db.Column(
        db.String(30),
        nullable=True
    )

    tipo_contenido = db.Column(
        db.Integer,
        nullable=True
    )

    contenido_url = db.Column(
        db.Text,
        nullable=True
    )

    
    # Objeto
    def __init__(self,
                 titulo,
                 portada_url,
                 referencia,
                 tipo_contenido,
                 contenido_url):
        self.titulo = titulo
        self.portada_url = portada_url
        self.referencia = referencia
        self.tipo_contenido = tipo_contenido
        self.contenido_url = contenido_url