from utils.db import db

class RecursoEstudiado(db.Model):
    __tablename__ = 'recurso_estudiado'

    # Características
    id_usuario = db.Column(
        db.Integer,
        primary_key=True,
        nullable=True
    )

    id_recurso = db.Column(
        db.Integer,
        db.ForeignKey('recurso_educativo.id_recurso'),
        primary_key=True,
        nullable=True
    )

    nota_actual = db.Column(
        db.Integer,
        nullable=True
    )

    aprobacion = db.Column(
        db.Boolean,
        nullable=True
    )


    # Objeto
    def __init__(self,
                 id_usuario,
                 id_recurso,
                 nota_actual,
                 aprobacion):
        self.id_usuario = id_usuario
        self.id_recurso = id_recurso
        self.nota_actual = nota_actual
        self.aprobacion = aprobacion