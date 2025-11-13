from utils.ma import ma
from marshmallow import post_dump
import random

from models.cuestionario import Cuestionario

# SCHEMA PARA CUESTIONARIO
class CuestionarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Cuestionario
        fields = (
            'id_cuestionario',
            'orden',
            'pregunta',
            'rpta_correcta',
            'rpta_incorrecta1',
            'rpta_incorrecta2',
            'rpta_incorrecta3',
        )
    
    # Post-procesar para mezclar respuestas
    @post_dump
    def mezclar_respuestas(self, data, **kwargs):
        """Mezcla las respuestas de manera aleatoria y crea un mapeo"""
        
        # Crear lista con tuplas (valor_respuesta, nombre_campo_original)
        respuestas_originales = [
            {'valor': data['rpta_correcta'], 'campo': 'rpta_correcta'},
            {'valor': data['rpta_incorrecta1'], 'campo': 'rpta_incorrecta1'},
            {'valor': data['rpta_incorrecta2'], 'campo': 'rpta_incorrecta2'},
            {'valor': data['rpta_incorrecta3'], 'campo': 'rpta_incorrecta3'}
        ]
        
        # Mezclar
        random.shuffle(respuestas_originales)
        
        # Crear dos listas: una para mostrar al usuario y otra para el mapeo
        data['respuestas'] = [r['valor'] for r in respuestas_originales]
        
        # ✅ IMPORTANTE: Mapeo entre índice de respuesta mostrada y campo original
        data['mapeo_respuestas'] = {
            i: r['campo'] for i, r in enumerate(respuestas_originales)
        }
        
        # Opcional: Eliminar las respuestas individuales
        del data['rpta_correcta']
        del data['rpta_incorrecta1']
        del data['rpta_incorrecta2']
        del data['rpta_incorrecta3']
        
        return data

# INSTANCIAS DE SCHEMAS
cuestionario_schema = CuestionarioSchema()
cuestionarios_schema = CuestionarioSchema(many=True)