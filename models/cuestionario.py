from utils.db import db

class Cuestionario(db.Model):
    __tablename__ = 'cuestionario'

    # Características
    id_cuestionario = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
        nullable=True
    )

    id_rec_edu = db.Column(
        db.Integer,
        db.ForeignKey('recurso_educativo.id_rec_edu'),
        nullable=True
    )

    orden = db.Column(
        db.Integer,
        nullable=True
    )

    pregunta = db.Column(
        db.String(100),
        nullable=True
    )

    rpta_correcta = db.Column(
        db.String(150),
        nullable=True
    )

    rpta_incorrecta1 = db.Column(
        db.String(150),
        nullable=True
    )

    rpta_incorrecta2 = db.Column(
        db.String(150),
        nullable=True
    )

    rpta_incorrecta3 = db.Column(
        db.String(150),
        nullable=True
    )

    
    # Objeto
    def __init__(self,
                 id_rec_edu,
                 orden,
                 pregunta,
                 rpta_correcta,
                 rpta_incorrecta1,
                 rpta_incorrecta2,
                 rpta_incorrecta3):
        self.id_rec_edu = id_rec_edu
        self.orden = orden
        self.pregunta = pregunta
        self.rpta_correcta = rpta_correcta
        self.rpta_incorrecta1 = rpta_incorrecta1
        self.rpta_incorrecta2 = rpta_incorrecta2
        self.rpta_incorrecta3 = rpta_incorrecta3