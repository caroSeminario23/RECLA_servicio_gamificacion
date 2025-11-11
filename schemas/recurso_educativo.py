from utils.ma import ma
from marshmallow import fields

from models.recurso_educativo import RecursoEducativo

# SCHEMA PARA RECURSO EDUCATIVO GENERAL
class RecursoEducativoPortadaSchema(ma.Schema):
    class Meta:
        fields = (
            'id_rec_edu',
            'titulo',
            'portada_url',
            'tipo_contenido',
            'resuelto',
            'porcentaje_acierto'
        )
    
    id_rec_edu = fields.Integer()
    titulo = fields.String()
    portada_url = fields.String()
    tipo_contenido = fields.Integer()
    resuelto = fields.Boolean()
    porcentaje_acierto = fields.Float()


# INSTANCIAS DE SCHEMAS
recurso_educativo_portada_schema = RecursoEducativoPortadaSchema()
recursos_educativos_portada_schema = RecursoEducativoPortadaSchema(many=True)


# CONTENIDO DE RECURSO EDUCATIVO
class RecursoEducativoContenidoSchema(ma.Schema):
    class Meta:
        fields = (
            'id_rec_edu',
            'referencia',
            'contenido_url',
        )

    id_rec_edu = fields.Integer()
    referencia = fields.String()
    contenido_url = fields.String()

# INSTANCIAS DE SCHEMAS
recurso_educativo_contenido_schema = RecursoEducativoContenidoSchema()
recursos_educativos_contenido_schema = RecursoEducativoContenidoSchema(many=True)



# SCHEMA PARA CUESTIONARIO
class RecursoEducativoCuestionarioSchema(ma.Schema):
    pass
    
    # Generar campos dinámicamente
for i in range(1, 5):
    setattr(RecursoEducativoCuestionarioSchema, f'RE_{i}_orden', fields.Integer())
    setattr(RecursoEducativoCuestionarioSchema, f'RE_{i}_pregunta', fields.String())
    setattr(RecursoEducativoCuestionarioSchema, f'RE_{i}_rpta_correcta', fields.String())
    setattr(RecursoEducativoCuestionarioSchema, f'RE_{i}_rpta_incorrecta1', fields.String())
    setattr(RecursoEducativoCuestionarioSchema, f'RE_{i}_rpta_incorrecta2', fields.String())
    setattr(RecursoEducativoCuestionarioSchema, f'RE_{i}_rpta_incorrecta3', fields.String())


# INSTANCIAS DE SCHEMAS
recurso_educativo_cuestionario_schema = RecursoEducativoCuestionarioSchema()
recursos_educativos_cuestionario_schema = RecursoEducativoCuestionarioSchema(many=True)


# SCHEMA PARA RESPUESTAS
class RecursoEducativoRespuestaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RecursoEducativo
        fields = (
            'id_rec_edu',
            'id_usuario',
            'rpta1',
            'rpta2',
            'rpta3',
            'rpta4',
        )
    
    id_rec_edu = fields.Integer()
    id_usuario = fields.Integer()
    rpta1 = fields.String()
    rpta2 = fields.String()
    rpta3 = fields.String()
    rpta4 = fields.String()

# INSTANCIAS DE SCHEMAS
recurso_educativo_respuesta_schema = RecursoEducativoRespuestaSchema()
recursos_educativos_respuesta_schema = RecursoEducativoRespuestaSchema(many=True)