from utils.ma import ma
#from marshmallow import fields

from models.insignia import Insignia

# SCHEMAS
class InsigniaConsultaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Insignia
        fields = (
            'id_insignia',
            'nombre',
            'url_imagen',
            'nivel'
        )

class InsigniaDetalleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Insignia
        fields = (
            'id_insignia',
            'ptos_necesarios',
            'tipo_ptos'
        )


# INSTANCIAS DE SCHEMAS
insignia_schema_consulta = InsigniaConsultaSchema()
insignias_schema_consulta = InsigniaConsultaSchema(many=True)
insignia_schema_detalle = InsigniaDetalleSchema()
insignias_schema_detalle = InsigniaDetalleSchema(many=True)