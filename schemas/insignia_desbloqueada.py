from utils.ma import ma
from marshmallow import fields


class InsigniaConEstadoSchema(ma.Schema):
    class Meta:
        fields = (
            'id_insignia',
            'nombre', 
            'url_imagen',
            'nivel',
            'id_usuario',
            'desbloqueado'
        )
    
    id_insignia = fields.Integer()
    nombre = fields.String()
    url_imagen = fields.String()
    nivel = fields.Integer()
    id_usuario = fields.Integer()
    desbloqueado = fields.Boolean()


# INSTANCIAS DE SCHEMAS
insignia_con_estado_schema = InsigniaConEstadoSchema()
insignias_con_estado_schema = InsigniaConEstadoSchema(many=True)