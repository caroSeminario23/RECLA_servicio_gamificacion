from utils.ma import ma
from marshmallow import fields

from models.recurso_educativo import RecursoEducativo

# SCHEMA PARA RECURSO EDUCATIVO GENERAL
class RecursoEducativoGeneralSchema(ma.Schema):
    class Meta:
        fields = (
            'id_rec_edu',
            'titulo',
            'portada_url',
            'referencia',
            'tipo_contenido',
            'contenido_url',
            'puntaje_ultimo'
        )
    
    id_rec_edu = fields.Integer()
    titulo = fields.String()
    portada_url = fields.String()
    referencia = fields.String()
    tipo_contenido = fields.Integer()
    contenido_url = fields.String()
    puntaje_ultimo = fields.Integer()


# INSTANCIAS DE SCHEMAS
recurso_educativo_schema = RecursoEducativoGeneralSchema()
recursos_educativos_schema = RecursoEducativoGeneralSchema(many=True)


# SCHEMA PARA CUESTIONARIO
class RecursoEducativoCuestionarioSchema(ma.Schema):
    class Meta:
        fields = tuple(
            f'{i}_{field}'
            for i in range(1, 5)
            for field in [
                'orden',
                'pregunta',
                'rpta_correcta',
                'rpta_incorrecta1',
                'rpta_incorrecta2',
                'rpta_incorrecta3',
            ]
        )
    
    # Generar campos dinámicamente
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 5):
            self.fields[f'{i}_orden'] = fields.Integer()
            self.fields[f'{i}_pregunta'] = fields.String()
            self.fields[f'{i}_rpta_correcta'] = fields.String()
            self.fields[f'{i}_rpta_incorrecta1'] = fields.String()
            self.fields[f'{i}_rpta_incorrecta2'] = fields.String()
            self.fields[f'{i}_rpta_incorrecta3'] = fields.String()

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