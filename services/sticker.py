from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text

from utils.db import db
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