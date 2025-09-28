from utils.ma import ma
from marshmallow import fields

from models.recurso_educativo import RecursoEducativo

# SCHEMAS
class RecursoEducativoConsultaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RecursoEducativo
        fields = (
            'id_recurso',
            'titulo',
            'tipo',
            'img_portada'
        )

class RecursoEducativoDetalleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RecursoEducativo
        fields = (
            'id_recurso',
            'autor',
            'fuente_url',
        )