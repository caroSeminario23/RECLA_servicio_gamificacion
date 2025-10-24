from utils.ma import ma
from marshmallow import fields


class InsigniaConEstadoSchema(ma.Schema):
    class Meta:
        fields = (
            'id_insignia',
            'nombre', 
            'url_imagen',
            'nivel',
            'desbloqueado'
        )
    
    id_insignia = fields.Integer()
    nombre = fields.String()
    url_imagen = fields.String()
    nivel = fields.Integer()
    desbloqueado = fields.Boolean()


class InsigniaDesbloqueadaSchema(ma.Schema):
    class Meta:
        fields = (
            'id_insignia',
            'nombre',
            'url_imagen',
            'nivel'
        )
    
    id_insignia = fields.Integer()
    nombre = fields.String()
    url_imagen = fields.String()
    nivel = fields.Integer()


# INSTANCIAS DE SCHEMAS
insignia_con_estado_schema = InsigniaConEstadoSchema()
insignias_con_estado_schema = InsigniaConEstadoSchema(many=True)

insignia_desbloqueada_schema = InsigniaDesbloqueadaSchema()
insignias_desbloqueadas_schema = InsigniaDesbloqueadaSchema(many=True)