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
            'desbloqueado',
            'revisado',
            'nombre_insignia_1',
            'nombre_insignia_2',
            'nombre_insignia_3',
        )
    
    id_certificado = fields.Integer()
    nombre = fields.String()
    url_imagen = fields.String()
    nivel = fields.Integer()
    desbloqueado = fields.Boolean()
    revisado = fields.Boolean()
    nombre_insignia_1 = fields.String()
    nombre_insignia_2 = fields.String()
    nombre_insignia_3 = fields.String()


# INSTANCIAS DE SCHEMAS
certificado_con_estado_schema = CertificadoConEstadoSchema()
certificados_con_estado_schema = CertificadoConEstadoSchema(many=True)


class CertificadoCodValidacionSchema(ma.Schema):
    class Meta:
        fields = (
            'cod_validacion',
        )
    
    cod_validacion = fields.String()


# INSTANCIAS DE SCHEMAS
certificado_cod_validacion_schema = CertificadoCodValidacionSchema()
certificados_cod_validacion_schema = CertificadoCodValidacionSchema(many=True)



class CertificadoDesbloqueadoSchema(ma.Schema):
    class Meta:
        fields = (
            'id_certificado',
            'nombre',
            'url_imagen',
            'nivel',
        )
    
    id_certificado = fields.Integer()
    nombre = fields.String()
    url_imagen = fields.String()
    nivel = fields.Integer()


# INSTANCIAS DE SCHEMAS
certificado_desbloqueado_schema = CertificadoDesbloqueadoSchema()
certificados_desbloqueados_schema = CertificadoDesbloqueadoSchema(many=True)