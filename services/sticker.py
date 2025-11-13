from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import requests, time
from concurrent.futures import ThreadPoolExecutor

from utils.db import db
from utils.logger import get_logger
from utils.servicios_externos import VERIFICADOR_PUNTOS_STICKER, AUMENTAR_EXPERIENCIA
from models.sticker_desbloqueado import StickerDesbloqueado
from schemas.sticker_desbloqueado import stickers_con_estado_schema


# Configurar el logger
logger = get_logger(__name__)

sticker_routes = Blueprint('sticker_routes', __name__)


# PRESENTACIÓN DE STICKERS (INDICANDO LOS DESBLOQUEADOS)
@sticker_routes.route('/get_stickers_con_estado', methods=['POST'])
def get_stickers_con_estado():
    inicio_tiempo = time.time()
    try:
        # Validar que existe el JSON y el campo
        field_required = ['id_usuario', 'categoria']
        if not request.json or not all(field in request.json for field in field_required):
            return make_response(jsonify({
                'status': 400,
                'message': 'Faltan campos requeridos'
            }), 400)
            
        id_usuario = request.json.get('id_usuario')
        categoria = request.json.get('categoria')

        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_usuario no puede estar vacío'
            }), 400)
        
        if not categoria:
            return make_response(jsonify({
                'status': 400,
                'message': 'categoria no puede estar vacío'
            }), 400)
        
        consulta_stickers_con_estado = """
        SELECT
            S.id_sticker,  
            S.url_imagen, 
            S.precio,
            CASE 
                WHEN SD.id_sticker IS NOT NULL 
                THEN true
                ELSE false
            END as desbloqueado
        FROM sticker as S
        LEFT JOIN sticker_desbloqueado as SD
            ON S.id_sticker = SD.id_sticker 
            AND SD.id_usuario = :id_usuario
        WHERE S.categoria = :categoria
        ORDER BY S.id_sticker;
        """

        stickers_con_estado = db.session.execute(text(consulta_stickers_con_estado), {'id_usuario': id_usuario, 'categoria': categoria})

        resultado_raw = [dict(row._mapping) for row in stickers_con_estado]
        resultado = stickers_con_estado_schema.dump(resultado_raw)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"get_stickers_con_estado exitoso para usuario {id_usuario}, categoria {categoria}. Tiempo: {tiempo_respuesta:.3f}s")

        data = {
            "message": "Stickers con estado obtenidos correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_stickers_con_estado: {err}. Tiempo: {tiempo_respuesta:.3f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    
    
# AUMENTAR EXPERIENCIA AL USUARIO (POR DESBLOQUEO DE STICKER)
def _aumentar_experiencia_sticker(id_usuario):
    """Ejecuta en background sin bloquear la respuesta"""
    try:
        respuesta = requests.post(AUMENTAR_EXPERIENCIA, 
            json={'id_usuario': id_usuario, 'motivo': 3},
            timeout=3)
        if respuesta.status_code != 200:
            logger.error(f"Error aumentando experiencia: {respuesta.text}")
    except Exception as e:
        logger.error(f"Error en sticker background task: {e}")

# DESBLOQUEAR STICKER
@sticker_routes.route('/desbloquear_sticker', methods=['POST'])
def desbloquear_sticker():
    inicio_tiempo = time.time()
    try:
        # Validar que existe el JSON y los campos
        required_fields = ['id_sticker', 'id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'id_sticker e id_usuario son requeridos'
            }), 400)
        
        id_sticker = request.json.get('id_sticker')
        id_usuario = request.json.get('id_usuario')
        
        # Validar que no sean None o vacíos
        if not id_sticker or not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_sticker e id_usuario no pueden estar vacíos'
            }), 400)
        
        # Verificar que el usuario tenga el medio para pagarlo
        #sticker = Sticker.query.filter_by(id_sticker=id_sticker).first()
        sticker = db.session.execute(text("""
            SELECT precio
            FROM sticker
            WHERE id_sticker = :id_sticker
        """), {'id_sticker': id_sticker}).first()

        if not sticker:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Sticker no encontrado para desbloquar. Tiempo: {tiempo_respuesta:.3f}s")
            return make_response(jsonify({
                'status': 404,
                'message': 'Sticker no encontrado'
            }), 404)
        
        precio_sticker = sticker.precio

        logger.info(f"Verificando puntos para usuario {id_usuario}, sticker {id_sticker}, precio: {precio_sticker}")

        ## Llamar al servicio de usuario para verificar puntos
        servicio_verificador = VERIFICADOR_PUNTOS_STICKER

        respuesta_servicio = requests.post(
            servicio_verificador, 
            json={
                'id_usuario': id_usuario,
                'precio_sticker': precio_sticker
            },
            timeout=2
        )

        if respuesta_servicio.status_code != 200:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error verificando puntos en desbloquear_sticker. Usuario: {id_usuario}, Sticker: {id_sticker}. Respuesta: {respuesta_servicio.text}. Tiempo: {tiempo_respuesta:.3f}s")
            return make_response(jsonify({
                'status': respuesta_servicio.status_code,
                'message': 'Error verificando puntos con el servicio de usuario'
            }), respuesta_servicio.status_code)

        logger.info(f"Guardando sticker desbloqueado en BD para usuario {id_usuario}, sticker {id_sticker}")

        # Respuesta exitosa, proceder a desbloquear el sticker
        nuevo_sticker_desbloqueado = StickerDesbloqueado(
            id_usuario=id_usuario,
            id_sticker=id_sticker
        )

        try:
            db.session.add(nuevo_sticker_desbloqueado)
            db.session.commit()
            logger.info(f"Sticker guardado en BD para usuario {id_usuario}, sticker {id_sticker}")
        except IntegrityError as e:
            db.session.rollback()
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error de integridad en desbloquear_sticker (sticker ya desbloqueado). Usuario: {id_usuario}, Sticker: {id_sticker}. Tiempo: {tiempo_respuesta:.3f}s")
            return make_response(jsonify({
                'status': 400,
                'message': 'El sticker ya ha sido desbloqueado por este usuario'
            }), 400)
        
        logger.info(f"Aumentando experiencia para usuario {id_usuario}")

        # ⭐ Ejecutar experiencia en background (NO bloquea)
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(_aumentar_experiencia_sticker, id_usuario)
        
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"desbloquear_sticker exitoso para usuario {id_usuario}, sticker {id_sticker}. Tiempo: {tiempo_respuesta:.3f}s")

        # Respuesta exitosa, proceder a responder
        data = {
            'message': 'Sticker desbloqueado exitosamente',
            "status": 201
        }

        return make_response(jsonify(data), 201)
    
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en desbloquear_sticker: {err}. Tiempo: {tiempo_respuesta:.3f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)