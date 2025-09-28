from utils.ma import ma
from marshmallow import fields, validates, ValidationError

from models.certificado_desbloqueado import CertificadoDesbloqueado

class CertificadoConEstadoSchema(ma.Schema):
    class Meta:
        fields = (
            'id_certificado',
            'nombre', 
            'url_imagen',
            'nivel',
            'id_usuario',
            'desbloqueado'
        )
    
    id_certificado = fields.Integer()
    nombre = fields.String()
    url_imagen = fields.String()
    nivel = fields.Integer()
    id_usuario = fields.Integer()
    desbloqueado = fields.Boolean()


# INSTANCIAS DE SCHEMAS
certificado_con_estado_schema = CertificadoConEstadoSchema()
certificados_con_estado_schema = CertificadoConEstadoSchema(many=True)