from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import requests

from utils.db import db
from utils.servicios_externos import VERIFICADOR_PUNTOS_STICKER, AUMENTAR_EXPERIENCIA
from models.sticker import Sticker
from models.sticker_desbloqueado import StickerDesbloqueado
from schemas.sticker_desbloqueado import stickers_con_estado_schema

sticker_routes = Blueprint('sticker_routes', __name__)


# PRESENTACIÓN DE STICKERS (INDICANDO LOS DESBLOQUEADOS)
@sticker_routes.route('/get_stickers_con_estado', methods=['POST'])
def get_stickers_con_estado():
    try:
        # Validar que existe el JSON y el campo
        if not request.json or 'id_usuario' not in request.json:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_usuario es requerido'
            }), 400)
            
        id_usuario = request.json.get('id_usuario')
        
        # Validar que no sea None o vacío
        if not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_usuario no puede estar vacío'
            }), 400)
        
    except Exception as err:
        print(f"Error en get_stickers_con_estado: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    
    consulta_stickers_con_estado = """
    SELECT
        S.id_sticker,  
        S.url_imagen, 
        S.precio,
        S.categoria,
        COALESCE(SD.id_usuario, :id_usuario) as id_usuario,
        CASE 
            WHEN SD.id_sticker IS NOT NULL 
            THEN true
            ELSE false
        END as desbloqueado
    FROM sticker as S
    LEFT JOIN sticker_desbloqueado as SD
        ON S.id_sticker = SD.id_sticker 
        AND SD.id_usuario = :id_usuario
    ORDER BY S.id_sticker;
    """

    stickers_con_estado = db.session.execute(text(consulta_stickers_con_estado), {'id_usuario': id_usuario})

    resultado_raw = [dict(row._mapping) for row in stickers_con_estado]
    resultado = stickers_con_estado_schema.dump(resultado_raw)

    data = {
        "message": "Stickers con estado obtenidos correctamente",
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)


# DESBLOQUEAR STICKER
@sticker_routes.route('/desbloquear_sticker', methods=['POST'])
def desbloquear_sticker():
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
        sticker = Sticker.query.filter_by(id_sticker=id_sticker).first()
        if not sticker:
            return make_response(jsonify({
                'status': 404,
                'message': 'Sticker no encontrado'
            }), 404)
        
        precio_sticker = sticker.precio

        ## Llamar al servicio de usuario para verificar puntos
        servicio_verificador = VERIFICADOR_PUNTOS_STICKER

        respuesta_servicio = requests.post(servicio_verificador, json={
            'id_usuario': id_usuario,
            'precio_sticker': precio_sticker
        })

        if respuesta_servicio.status_code != 200:
            return make_response(jsonify({
                'status': respuesta_servicio.status_code,
                'message': 'Error verificando puntos con el servicio de usuario'
            }), respuesta_servicio.status_code)

        # Respuesta exitosa, proceder a desbloquear el sticker
        nuevo_sticker_desbloqueado = StickerDesbloqueado(
            id_usuario=id_usuario,
            id_sticker=id_sticker
        )

        try:
            db.session.add(nuevo_sticker_desbloqueado)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return make_response(jsonify({
                'status': 400,
                'message': 'El sticker ya ha sido desbloqueado por este usuario'
            }), 400)
        
        # Llamar al servicio para que aumente puntos de experiencia al usuario
        servicio_experiencia = AUMENTAR_EXPERIENCIA

        respuesta_experiencia = requests.post(servicio_experiencia, json={
            'id_usuario': id_usuario,
            'motivo': 3  # Motivo 3: Desbloqueo de sticker
        })

        if respuesta_experiencia.status_code != 200:
            return make_response(jsonify({
                'status': respuesta_experiencia.status_code,
                'message': 'Error aumentando experiencia con el servicio de usuario'
            }), respuesta_experiencia.status_code)
        
        # Respuesta exitosa, proceder a responder
        data = {
            'message': 'Sticker desbloqueado exitosamente',
            "status": 201
        }

        return make_response(jsonify(data), 201)
    
    except Exception as err:
        print(f"Error en desbloquear_sticker: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)