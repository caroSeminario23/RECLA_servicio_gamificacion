from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import requests, time
from concurrent.futures import ThreadPoolExecutor

from models.cuestionario import Cuestionario
from utils.db import db
from utils.logger import get_logger
from utils.servicios_externos import (AUMENTAR_CONTADORES,
                                      AUMENTAR_EXPERIENCIA_RECURSO_EDUCATIVO, VERIFICADOR_ACTIVIDAD_DIARIA)
from models.recurso_educativo import RecursoEducativo
from schemas.recurso_educativo import (recursos_educativos_portada_schema,
                                       recurso_educativo_contenido_schema,
                                       resultado_recurso_educativo_schema)
from schemas.cuestionario import cuestionarios_schema
from models.re_resuelto import REResuelto

# Configurar el logger
logger = get_logger(__name__)

recurso_educativo_routes = Blueprint('recurso_educativo_routes', __name__)

# PRESENTACIÓN DE PORTADAS DE RECURSOS EDUCATIVOS
'''
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
            ROUND((
                (
                    (CASE WHEN RR.rpta1 = 'rpta_correcta' THEN 1 ELSE 0 END) +
                    (CASE WHEN RR.rpta2 = 'rpta_correcta' THEN 1 ELSE 0 END) +
                    (CASE WHEN RR.rpta3 = 'rpta_correcta' THEN 1 ELSE 0 END) +
                    (CASE WHEN RR.rpta4 = 'rpta_correcta' THEN 1 ELSE 0 END)
                ) * 100.0 / 4
            ), 2) as porcentaje_acierto
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
        GROUP BY RE.id_rec_edu, RE.titulo, RE.portada_url, RE.referencia, RE.tipo_contenido, RE.contenido_url, RR.id_rec_edu, RR.rpta1, RR.rpta2, RR.rpta3, RR.rpta4;
        """

        portadas_rec_edus = db.session.execute(text(consulta_rec_educativos), {'id_usuario': id_usuario}).mappings().fetchall()

        resultados_raw = [dict(row) for row in portadas_rec_edus]
        resultados = recursos_educativos_portada_schema.dump(resultados_raw)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"Presentación de portadas de recursos educativos para id_usuario {id_usuario} completada en {tiempo_respuesta:.3f} segundos.")

        data = {
            "message": "Portadas de recursos educativos obtenidas correctamente",
            "status": 200,
            "data": resultados
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error al presentar portadas de recursos educativos para id_usuario {id_usuario}: {str(err)} - Tiempo de respuesta: {tiempo_respuesta:.3f} segundos.")
        return make_response(jsonify({
            "message": "Error al obtener portadas de recursos educativos",
            "status": 500,
            "error": str(err)
        }), 500)
'''

# VERSIÓN OPTIMIZADA DE PRESENTACION DE PORTADAS DE RECURSOS EDUCATIVOS
@recurso_educativo_routes.route('/portadas_recursos_educativos', methods=['POST'])
def presentar_portadas_recursos_educativos():
    inicio_tiempo = time.perf_counter()

    try:
        data_in = request.json
        #1. Validación rápida de entrada
        if not data_in:
             return make_response(jsonify({'status': 400, 'message': 'JSON requerido'}), 400)
        
        id_usuario = data_in.get('id_usuario')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'El campo id_usuario no puede estar vacío'
            }), 400)
        
        # 2. Consulta optimizada
        consulta_rec_educativos = """
        WITH UltimoIntento AS (
            SELECT 
                id_rec_edu,
                rpta1, rpta2, rpta3, rpta4,
                ROW_NUMBER() OVER (
                    PARTITION BY id_rec_edu 
                    ORDER BY fec_resolucion DESC
                ) as rn
            FROM RE_RESUELTO
            WHERE id_usuario = :id_usuario
        )
        SELECT 
            RE.id_rec_edu,
            RE.titulo,
            RE.portada_url,
            RE.tipo_contenido,
            CASE 
                WHEN UI.id_rec_edu IS NOT NULL THEN True
                ELSE False
            END as resuelto,
            CAST(ROUND((
                (
                    (CASE WHEN UI.rpta1 = 'rpta_correcta' THEN 1 ELSE 0 END) +
                    (CASE WHEN UI.rpta2 = 'rpta_correcta' THEN 1 ELSE 0 END) +
                    (CASE WHEN UI.rpta3 = 'rpta_correcta' THEN 1 ELSE 0 END) +
                    (CASE WHEN UI.rpta4 = 'rpta_correcta' THEN 1 ELSE 0 END)
                ) * 100.0 / 4
            ), 2) AS FLOAT) as porcentaje_acierto
        FROM RECURSO_EDUCATIVO RE
        LEFT JOIN UltimoIntento UI 
            ON RE.id_rec_edu = UI.id_rec_edu 
            AND UI.rn = 1 -- Solo tomamos el intento más reciente (fila 1)
        ORDER BY RE.id_rec_edu;    
        """

        portadas_rec_edus = db.session.execute(text(consulta_rec_educativos), {'id_usuario': id_usuario}).mappings().fetchall()
        resultados_raw = [dict(row) for row in portadas_rec_edus]

        tiempo_respuesta = time.perf_counter() - inicio_tiempo
        logger.info(f"Presentación de portadas de recursos educativos para id_usuario {id_usuario} completada en {tiempo_respuesta:.3f} segundos.")

        data = {
            "message": "Portadas de recursos educativos obtenidas correctamente",
            "status": 200,
            "data": resultados_raw
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.perf_counter() - inicio_tiempo
        logger.error(f"Error al presentar portadas de recursos educativos para id_usuario {id_usuario}: {str(err)} - Tiempo de respuesta: {tiempo_respuesta:.3f} segundos.")
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
        logger.info(f"Presentación de detalle de recurso educativo {id_rec_edu} completada en {tiempo_respuesta:.3f} segundos.")

        data = {
            "message": "Detalle de recurso educativo obtenido correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en presentar_detalle_recurso_educativo: {err}. Tiempo: {tiempo_respuesta:.3f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# CARGAR PREGUNTAS DEL CUESTIONARIO DE UN RECURSO EDUCATIVO
@recurso_educativo_routes.route('/cargar_cuestionario_recurso_educativo', methods=['POST'])
def cargar_cuestionario_recurso_educativo():
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
        
        # Obtener preguntas del cuestionario
        preguntas_cuestionario = Cuestionario.query.filter_by(id_rec_edu=id_rec_edu).all()

        if not preguntas_cuestionario:
            return make_response(jsonify({
                'status': 404,
                'message': 'Cuestionario no encontrado'
            }), 404)

        resultado = cuestionarios_schema.dump(preguntas_cuestionario)
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"Carga de cuestionario de recurso educativo {id_rec_edu} completada en {tiempo_respuesta:.3f} segundos.")

        data = {
            "message": "Cuestionario de recurso educativo obtenido correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en cargar_cuestionario_recurso_educativo: {err}. Tiempo: {tiempo_respuesta:.3f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    


# AUMENTAR PUNTOS DE EXPERIENCIA (en paralelo)
def _aumentar_experiencia(id_usuario, puntos_experiencia):
    try:
        requests.post(
            AUMENTAR_EXPERIENCIA_RECURSO_EDUCATIVO,
            json={'id_usuario': id_usuario, 'ptos_experiencia': puntos_experiencia},
            timeout=5
        )
        logger.info(f"Experiencia aumentada: {puntos_experiencia} puntos para usuario {id_usuario}")
    except Exception as ext_err:
        logger.error(f"Error al aumentar experiencia: {str(ext_err)}")

# AUMENTAR CONTADOR DE RECURSO EDUCATIVO (en paralelo)
def _aumentar_contador(id_rec_edu, id_usuario):
    try:
        requests.post(
            AUMENTAR_CONTADORES,
            json={'id_usuario': id_usuario, 'motivo': 3},
            timeout=5
        )
        logger.info(f"Contador aumentado para recurso {id_rec_edu}")
    except Exception as ext_err:
        logger.error(f"Error al aumentar contador: {str(ext_err)}")


# REGISTRAR ACTIVIDAD DIARIA EN BACKGROUND
def _registrar_actividad_diaria(id_usuario):
    """Ejecuta en background sin bloquear la respuesta"""
    try:
        respuesta = requests.post(VERIFICADOR_ACTIVIDAD_DIARIA, 
            json={'id_usuario': id_usuario},
            timeout=3)
        if respuesta.status_code != 201:
            logger.error(f"Error al registrar actividad diaria: {respuesta.text}")
    except Exception as e:
        logger.error(f"Error en registrar actividad diaria background task: {e}")


# GUARDAR RESPUESTAS DEL CUESTIONARIO DE UN RECURSO EDUCATIVO
@recurso_educativo_routes.route('/guardar_respuestas_cuestionario', methods=['POST'])
def guardar_respuestas_cuestionario():
    inicio_tiempo = time.time()
    
    try:
        required_fields = ['id_usuario', 'id_rec_edu', 'respuestas']
        
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'Faltan campos requeridos'
            }), 400)
        
        id_usuario = request.json['id_usuario']
        id_rec_edu = request.json['id_rec_edu']
        respuestas_usuario = request.json['respuestas']  # Debe contener el mapeo
        
        # ✅ Validar que no sean None o vacíos
        if not id_usuario or not id_rec_edu or not respuestas_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'Los campos id_usuario, id_rec_edu y respuestas no pueden estar vacíos'
            }), 400)
        
        """
        Formato esperado de respuestas:
        {
            "1": "rpta_correcta",      # Pregunta orden 1
            "2": "rpta_incorrecta1",   # Pregunta orden 2
            "3": "rpta_incorrecta",   # Pregunta orden 3
            "4": "rpta_incorrecta2"    # Pregunta orden 4
        }
        """

        # ✅ Mapear respuestas: orden -> nombre_campo
        rpta1 = respuestas_usuario.get('1', '')
        rpta2 = respuestas_usuario.get('2', '')
        rpta3 = respuestas_usuario.get('3', '')
        rpta4 = respuestas_usuario.get('4', '')
        
        # ✅ Validar que todas las respuestas fueron proporcionadas
        if not all([rpta1, rpta2, rpta3, rpta4]):
            return make_response(jsonify({
                'status': 400,
                'message': 'Todas las 4 respuestas son requeridas'
            }), 400)
        
        # Crear registro en BD
        re_resuelto = REResuelto(
            id_rec_edu=id_rec_edu,
            id_usuario=id_usuario,
            rpta1=rpta1,
            rpta2=rpta2,
            rpta3=rpta3,
            rpta4=rpta4
        )


        # Buscar si ya existe un registro para este usuario y recurso educativo
        antes_resuelto = False

        existing_record = REResuelto.query.filter_by(id_usuario=id_usuario, id_rec_edu=id_rec_edu).first()
        if existing_record:
            antes_resuelto = True
        
        db.session.add(re_resuelto)
        db.session.commit()
        
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"Respuestas guardadas para usuario {id_usuario}, recurso {id_rec_edu}. Tiempo: {tiempo_respuesta:.3f}s")


        # ✅ CALCULAR PUNTOS DE EXPERIENCIA
        rptas_correctas = sum(1 for rpta in [rpta1, rpta2, rpta3, rpta4] if rpta == 'rpta_correcta')

        if antes_resuelto == False:
            # Tabla de puntos según respuestas correctas
            puntos_tabla = {
                0: 5,
                1: 13,
                2: 25,
                3: 38,
                4: 50
            }
        
        else:
            # Tabla de puntos según respuestas correctas
            puntos_tabla = {
                0: 2,
                1: 6,
                2: 12,
                3: 19,
                4: 25
            }
        
        # Obtener puntos de experiencia (5 es valor por defecto)
        puntos_experiencia = puntos_tabla.get(rptas_correctas, 5)

        # AUMENTAR PUNTOS DE EXPERIENCIA
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(_aumentar_experiencia, id_usuario, puntos_experiencia)
            executor.submit(_aumentar_contador, id_rec_edu, id_usuario)
            executor.submit(_registrar_actividad_diaria, id_usuario)

        resultado = resultado_recurso_educativo_schema.dump({
            'respuestas_correctas': rptas_correctas,
            'puntos_experiencia': puntos_experiencia
        })

        logger.info(f"Puntos de experiencia calculados: {puntos_experiencia} para usuario {id_usuario} - Respuestas correctas: {rptas_correctas} - Tiempo: {tiempo_respuesta:.3f}s")

        return make_response(jsonify({
            'status': 201,
            'message': 'Respuestas guardadas correctamente',
            'data': resultado
        }), 201)
    
    except Exception as err:
        db.session.rollback()
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error al guardar respuestas para usuario {id_usuario}, recurso {id_rec_edu}: {str(err)} - Tiempo: {tiempo_respuesta:.3f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error al guardar respuestas',
            'error': str(err)
        }), 500)