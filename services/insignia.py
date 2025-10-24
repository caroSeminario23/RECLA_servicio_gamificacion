from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import requests
import time

from utils.db import db
from utils.logger import get_logger
from utils.servicios_externos import VERIFICADOR_PUNTOS_INSIGNIA, AUMENTAR_EXPERIENCIA
from models.insignia import Insignia
from models.insignia_desbloqueada import InsigniaDesbloqueada
from schemas.insignia import insignia_schema_detalle
from schemas.insignia_desbloqueada import (insignias_con_estado_schema, 
                                           insignias_desbloqueadas_schema)

# Configurar el logger
logger = get_logger(__name__)

insignia_routes = Blueprint('insignia_routes', __name__)


# PRESENTACIÓN DE INSIGNIAS (INDICANDO LAS DESBLOQUEADAS)
@insignia_routes.route('/get_insignias_con_estado', methods=['POST'])
def get_insignias_con_estado():
    inicio_tiempo = time.time()
    try:
        # Validar que existe el JSON y el campo
        required_fields = ['id_usuario', 'tipo_ptos']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'Faltan campos requeridos (id_usuario, tipo_ptos)'
            }), 400)
            
        id_usuario = request.json.get('id_usuario')
        tipo_ptos = request.json.get('tipo_ptos')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_usuario no puede estar vacío'
            }), 400)

        if not tipo_ptos:
            return make_response(jsonify({
                'status': 400,
                'message': 'tipo_ptos no puede estar vacío'
            }), 400)

        consulta_insignias_con_estado = """
        SELECT 
            I.id_insignia, 
            I.nombre, 
            I.url_imagen, 
            I.nivel,
            CASE 
                WHEN ID.id_insignia IS NOT NULL 
                THEN true
                ELSE false
            END as desbloqueado
        FROM insignia as I
        LEFT JOIN insignia_desbloqueada as ID 
            ON I.id_insignia = ID.id_insignia 
            AND ID.id_usuario = :id_usuario
        WHERE I.tipo_ptos = :tipo_ptos
        ORDER BY I.id_insignia;
        """

        insignias_con_estado = db.session.execute(text(consulta_insignias_con_estado), {'id_usuario': id_usuario, 'tipo_ptos': tipo_ptos}).fetchall()

        resultado_raw = [dict(row._mapping) for row in insignias_con_estado]
        resultado = insignias_con_estado_schema.dump(resultado_raw)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"get_insignias_con_estado exitoso para usuario {id_usuario}, tipo_ptos {tipo_ptos}. Tiempo: {tiempo_respuesta:.2f}s")

        data = {
            "message": "Insignias obtenidas correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_insignias_con_estado: {err}. Tiempo: {tiempo_respuesta:.2f}s")
        return make_response(jsonify({
            'status': 400,
            'message': 'Error procesando la solicitud'
        }), 400)


# CONSULTAR DETALLE DE UNA INSIGNIA
@insignia_routes.route('/get_detalle_insignia', methods=['POST'])
def get_detalle_insignia():
    inicio_tiempo = time.time()
    try:
        # Validar que existe el JSON y el campo
        if not request.json or 'id_insignia' not in request.json:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_insignia es requerido'
            }), 400)

        id_insignia = request.json.get('id_insignia')

        # Validar que no sea None o vacío
        if not id_insignia:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_insignia no puede estar vacío'
            }), 400)
        
        insignia = Insignia.query.filter_by(id_insignia=id_insignia).first()

        if not insignia:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Insignia no encontrada: {id_insignia}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 404,
                'message': 'Insignia no encontrada'
            }), 404)

        resultado = insignia_schema_detalle.dump(insignia)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"get_detalle_insignia exitoso para insignia {id_insignia}. Tiempo: {tiempo_respuesta:.2f}s")

        data = {
            "message": "Detalle de insignia obtenido correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_detalle_insignia: {err}. Tiempo: {tiempo_respuesta:.2f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# DESBLOQUEAR INSIGNIA (CANJEAR)
@insignia_routes.route('/desbloquear_insignia', methods=['POST'])
def desbloquear_insignia():
    inicio_tiempo = time.time()
    try:
        # Validar que existe el JSON y el campo
        required_fields = ['id_insignia', 'id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'id_insignia e id_usuario son requeridos'
            }), 400)

        id_insignia = request.json.get('id_insignia')
        id_usuario = request.json.get('id_usuario')

        # Validar que no sea None o vacío
        if not id_insignia or not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_insignia e id_usuario no pueden estar vacíos'
            }), 400)
        
        # Verificar que el usuario tenga el medio para pagarlo
        insignia = Insignia.query.filter_by(id_insignia=id_insignia).first()
        if not insignia:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Insignia no encontrada para desbloquear: {id_insignia}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 404,
                'message': 'Insignia no encontrada'
            }), 404)
        
        tipo_insignia = insignia.tipo_ptos
        precio_insignia = insignia.ptos_necesarios

        logger.info(f"Verificando puntos para usuario {id_usuario}, tipo_insignia: {tipo_insignia}, precio: {precio_insignia}")

        ## Llamar al servicio de usuario para verificar puntos (si tiene suficientes los resta)
        servicio_verificador = VERIFICADOR_PUNTOS_INSIGNIA
        
        respuesta_servicio = requests.post(servicio_verificador, json={
            'id_usuario': id_usuario,
            'tipo_insignia': tipo_insignia,
            'precio_insignia': precio_insignia
        })

        if respuesta_servicio.status_code != 200:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error verificando puntos en desbloquear_insignia. Usuario: {id_usuario}, Insignia: {id_insignia}. Respuesta: {respuesta_servicio.text}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': respuesta_servicio.status_code,
                'message': 'Error verificando puntos con el servicio de usuario'
            }), respuesta_servicio.status_code)
        
        # Respuesta exitosa, proceder a desbloquear la insignia
        nueva_insignia_desbloqueada = InsigniaDesbloqueada(
            id_usuario=id_usuario,
            id_insignia=id_insignia
        )

        try:
            db.session.add(nueva_insignia_desbloqueada)
            db.session.commit()
            logger.info(f"Insignia guardada en BD para usuario {id_usuario}, insignia {id_insignia}")
        except IntegrityError as e:
            db.session.rollback()
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error de integridad en desbloquear_insignia (ya existe o datos inválidos). Usuario: {id_usuario}, Insignia: {id_insignia}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 400,
                'message': 'La insignia ya está desbloqueada para este usuario o los datos son inválidos'
            }), 400)
        
        logger.info(f"Aumentando experiencia para usuario {id_usuario}")
        
        # Llamar al servicio para que aumente puntos de experiencia al usuario
        servicio_experiencia = AUMENTAR_EXPERIENCIA

        respuesta_experiencia = requests.post(servicio_experiencia, json={
            'id_usuario': id_usuario,
            'motivo': 1  # Motivo 1: Desbloqueo de insignia
        })

        if respuesta_experiencia.status_code != 200:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error aumentar experiencia en desbloquear_insignia. Usuario: {id_usuario}. Respuesta: {respuesta_experiencia.text}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': respuesta_experiencia.status_code,
                'message': 'Error aumentando experiencia con el servicio de usuario'
            }), respuesta_experiencia.status_code)
        
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"desbloquear_insignia exitoso para usuario {id_usuario}, insignia {id_insignia}. Tiempo: {tiempo_respuesta:.2f}s")

        # Respuesta exitosa, proceder a responder
        data = {
            "message": "Insignia desbloqueada correctamente",
            "status": 201
        }

        return make_response(jsonify(data), 201)

    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en desbloquear_insignia: {err}. Tiempo: {tiempo_respuesta:.2f}s")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    


# PRESENTACIÓN DE INSIGNIAS DE UN USUARIO (SOLO LAS DESBLOQUEADAS)
@insignia_routes.route('/get_insignias_con_estado_usuario', methods=['POST'])
def get_insignias_con_estado_usuario():
    inicio_tiempo = time.time()
    try:
        # Validar que existe el JSON y el campo
        required_fields = ['id_usuario', 'tipo_ptos']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'Faltan campos requeridos (id_usuario, tipo_ptos)'
            }), 400)
            
        id_usuario = request.json.get('id_usuario')
        tipo_ptos = request.json.get('tipo_ptos')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_usuario no puede estar vacío'
            }), 400)

        if not tipo_ptos:
            return make_response(jsonify({
                'status': 400,
                'message': 'tipo_ptos no puede estar vacío'
            }), 400)

        consulta_insignias_desbloqueadas = """
        SELECT 
            I.id_insignia, 
            I.nombre, 
            I.url_imagen, 
            I.nivel
        FROM insignia as I
        RIGHT JOIN insignia_desbloqueada as ID 
            ON I.id_insignia = ID.id_insignia 
            AND ID.id_usuario = :id_usuario
        WHERE I.tipo_ptos = :tipo_ptos
        ORDER BY I.id_insignia;
        """

        insignias_desbloqueadas = db.session.execute(text(consulta_insignias_desbloqueadas), {'id_usuario': id_usuario, 'tipo_ptos': tipo_ptos}).fetchall()

        resultado_raw = [dict(row._mapping) for row in insignias_desbloqueadas]
        resultado = insignias_desbloqueadas_schema.dump(resultado_raw)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"get_insignias_con_estado_usuario exitoso para usuario {id_usuario}, tipo_ptos {tipo_ptos}. Tiempo: {tiempo_respuesta:.2f}s")

        data = {
            "message": "Insignias obtenidas correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_insignias_con_estado_usuario: {err}. Tiempo: {tiempo_respuesta:.2f}s")
        return make_response(jsonify({
            'status': 400,
            'message': 'Error procesando la solicitud'
        }), 400)