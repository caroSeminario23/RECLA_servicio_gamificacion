from utils.ma import ma
from marshmallow import fields, validates, ValidationError

from models.certificado import Certificado

# SCHEMAS
class CertificadoConsultaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Certificado
        fields = (
            'id_certificado',
            'nombre',
            'url_imagen',
            'nivel'
        )

class CertificadoDetalleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Certificado
        fields = (
            'id_certificado',
            'req_insignia_1_nombre',
            'req_insignia_2_nombre',
            'req_insignia_3_nombre'
        )

    req_insignia_1_nombre = fields.Function(
        lambda obj: obj.req_insignia_1.nombre if obj.req_insignia_1 else None
    )
    req_insignia_2_nombre = fields.Function(
        lambda obj: obj.req_insignia_2.nombre if obj.req_insignia_2 else None
    )
    req_insignia_3_nombre = fields.Function(
        lambda obj: obj.req_insignia_3.nombre if obj.req_insignia_3 else None
    )


# INSTANCIAS DE SCHEMAS
certificado_consulta_schema = CertificadoConsultaSchema()
certificados_consulta_schema = CertificadoConsultaSchema(many=True)
certificado_detalle_schema = CertificadoDetalleSchema()
certificados_detalle_schema = CertificadoDetalleSchema(many=True)