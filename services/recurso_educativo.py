from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import requests, time
from concurrent.futures import ThreadPoolExecutor

from utils.db import db
from utils.logger import get_logger
from utils.servicios_externos import AUMENTAR_CONTADOR_RECURSO_EDUCATIVO
from models.recurso_educativo import RecursoEducativo
from schemas.recurso_educativo import recursos_educativos_portada_schema, recurso_educativo_contenido_schema

# Configurar el logger
logger = get_logger(__name__)

recurso_educativo_routes = Blueprint('recurso_educativo_routes', __name__)

# PRESENTACIÓN DE PORTADAS DE RECURSOS EDUCATIVOS
@recurso_educativo_routes.route('/portadas_recursos_educativos', methods=['POST'])
def presentar_portadas_recursos_educativos():
    inicio_tiempo = time.time()

    try:
        # Validar que existe el JSON y el campo
        required_fields = ['id_usuario']

        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'Faltan campos requeridos (id_usuario)'
            }), 400)
        
        id_usuario = request.json['id_usuario']

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'El campo id_usuario no puede estar vacío'
            }), 400)
        
        # Consulta personalizada
        consulta_rec_educativos = """
        SELECT 
            RE.id_rec_edu,
            RE.titulo,
            RE.portada_url,
            RE.tipo_contenido,
            CASE 
                WHEN RR.id_rec_edu IS NOT NULL THEN True
                ELSE False
            END as resuelto,
            ROUND((COUNT(CASE 
                WHEN RR.rpta1 = 'rpta_correcta'
                THEN 1 
            END) * 100.0 / 4), 2) as porcentaje_acierto
        FROM RECURSO_EDUCATIVO RE
        LEFT JOIN RE_RESUELTO RR ON RE.id_rec_edu = RR.id_rec_edu
            AND RR.id_usuario = :id_usuario
            AND RR.fec_resolucion = (
                SELECT MAX(fec_resolucion) 
                FROM RE_RESUELTO 
                WHERE id_usuario = :id_usuario
                AND id_rec_edu = RE.id_rec_edu
            )
        LEFT JOIN CUESTIONARIO C1 ON RE.id_rec_edu = C1.id_rec_edu AND C1.orden = 1
        LEFT JOIN CUESTIONARIO C2 ON RE.id_rec_edu = C2.id_rec_edu AND C2.orden = 2
        LEFT JOIN CUESTIONARIO C3 ON RE.id_rec_edu = C3.id_rec_edu AND C3.orden = 3
        LEFT JOIN CUESTIONARIO C4 ON RE.id_rec_edu = C4.id_rec_edu AND C4.orden = 4
        GROUP BY RE.id_rec_edu, RE.titulo, RE.portada_url, RE.referencia, RE.tipo_contenido, RE.contenido_url, RR.id_rec_edu;
        """

        portadas_rec_edus = db.session.execute(text(consulta_rec_educativos), {'id_usuario': id_usuario}).mappings().fetchall()

        resultados_raw = [dict(row) for row in portadas_rec_edus]
        resultados = recursos_educativos_portada_schema.dump(resultados_raw)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"Presentación de portadas de recursos educativos para id_usuario {id_usuario} completada en {tiempo_respuesta:.4f} segundos.")

        data = {
            "message": "Portadas de recursos educativos obtenidas correctamente",
            "status": 200,
            "data": resultados
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error al presentar portadas de recursos educativos para id_usuario {id_usuario}: {str(err)} - Tiempo de respuesta: {tiempo_respuesta:.4f} segundos.")
        return make_response(jsonify({
            "message": "Error al obtener portadas de recursos educativos",
            "status": 500,
            "error": str(err)
        }), 500)


# PRESENTACIÓN DE CONTENIDO DE UN RECURSO EDUCATIVO
@recurso_educativo_routes.route('/detalle_recurso_educativo', methods=['POST'])
def presentar_detalle_recurso_educativo():
    inicio_tiempo = time.time()

    try:
        # Validar que existe el JSON y los campos
        required_fields = ['id_rec_edu']

        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'Faltan campos requeridos (id_rec_edu)'
            }), 400)
        
        id_rec_edu = request.json['id_rec_edu']

        # Validar que no sean None o vacíos
        if not id_rec_edu:
            return make_response(jsonify({
                'status': 400,
                'message': 'El campo id_rec_edu no puede estar vacío'
            }), 400)
        
        # Obtener el recurso educativo
        recurso_educativo = RecursoEducativo.query.get(id_rec_edu)

        if not recurso_educativo:
            return make_response(jsonify({
                'status': 404,
                'message': 'Recurso educativo no encontrado'
            }), 404)

        resultado = recurso_educativo_contenido_schema.dump(recurso_educativo)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"Presentación de detalle de recurso educativo {id_rec_edu} completada en {tiempo_respuesta:.4f} segundos.")

        data = {
            "message": "Detalle de recurso educativo obtenido correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en presentar_detalle_recurso_educativo: {err}. Tiempo: {tiempo_respuesta:.2f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)