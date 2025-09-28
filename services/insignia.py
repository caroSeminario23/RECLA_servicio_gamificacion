from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text

from utils.db import db
from models.insignia import Insignia
from schemas.insignia import insignia_schema_detalle
from schemas.insignia_desbloqueada import insignias_con_estado_schema

insignia_routes = Blueprint('insignia_routes', __name__)


# PRESENTACIÓN DE INSIGNIAS (INDICANDO LAS DESBLOQUEADAS)
@insignia_routes.route('/get_insignias_con_estado', methods=['POST'])
def get_insignias_con_estado():
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
        print(f"Error en get_certificados_con_estado: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 400,
            'message': 'Error procesando la solicitud'
        }), 400)

    consulta_insignias_con_estado = """
    SELECT 
        I.id_insignia, 
        I.nombre, 
        I.url_imagen, 
        I.nivel,
        COALESCE(ID.id_usuario, :id_usuario) as id_usuario,
        CASE 
            WHEN ID.id_insignia IS NOT NULL 
            THEN true
            ELSE false
        END as desbloqueado
    FROM insignia as I
    LEFT JOIN insignia_desbloqueada as ID 
        ON I.id_insignia = ID.id_insignia 
        AND ID.id_usuario = :id_usuario
    ORDER BY I.id_insignia;    
    """

    insignias_con_estado = db.session.execute(text(consulta_insignias_con_estado), {'id_usuario': id_usuario})

    resultado_raw = [dict(row._mapping) for row in insignias_con_estado]
    resultado = insignias_con_estado_schema.dump(resultado_raw)

    data = {
        "message": "Insignias obtenidas correctamente",
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)


# CONSULTAR DETALLE DE UNA INSIGNIA
@insignia_routes.route('/get_detalle_insignia', methods=['POST'])
def get_detalle_insignia():
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
            return make_response(jsonify({
                'status': 404,
                'message': 'Insignia no encontrada'
            }), 404)

        resultado = insignia_schema_detalle.dump(insignia)

        data = {
            "message": "Detalle de insignia obtenido correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:
        print(f"Error en get_detalle_insignia: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)