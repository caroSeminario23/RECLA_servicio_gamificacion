from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text

from utils.db import db
from utils.servicios_externos import AUMENTAR_EXPERIENCIA
from models.certificado import Certificado
from schemas.certificado import certificado_detalle_schema
from schemas.certificado_desbloqueado import certificado_con_estado_schema

certificado_routes = Blueprint('certificado_routes', __name__)


# PRESENTACIÓN DE CERTIFICADOS (INDICANDO LOS DESBLOQUEADOS)
@certificado_routes.route('/get_certificados_con_estado', methods=['POST'])
def get_certificados_con_estado():
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
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)

    consulta_certificados_con_estado = """
    SELECT 
        C.id_certificado, 
        C.nombre, 
        C.url_imagen, 
        C.nivel,
        C.revisado,
        COALESCE(CD.id_usuario, :id_usuario) as id_usuario,
        CASE 
            WHEN CD.id_certificado IS NOT NULL 
            THEN true
            ELSE false
        END as desbloqueado
    FROM certificado as C
    LEFT JOIN certificado_desbloqueado as CD 
        ON C.id_certificado = CD.id_certificado 
        AND CD.id_usuario = :id_usuario
    ORDER BY C.id_certificado;    
    """

    certificados_con_estado = db.session.execute(text(consulta_certificados_con_estado), {'id_usuario': id_usuario})

    resultado_raw = [dict(row._mapping) for row in certificados_con_estado]
    resultado = certificado_con_estado_schema.dump(resultado_raw)

    data = {
        'message': 'Certificados obtenidos exitosamente',
        "status": 200,
        "data": resultado
    }

    return make_response(jsonify(data), 200)


# CONSULTAR DETALLE DE UN CERTIFICADO
@certificado_routes.route('/get_detalle_certificado', methods=['POST'])
def get_detalle_certificado():
    try:
        # Validar que existe el JSON y los campos
        if not request.json or 'id_certificado' not in request.json:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_certificado es requerido'
            }), 400)
            
        id_certificado = request.json.get('id_certificado')
        
        # Validar que no sean None o vacíos
        if not id_certificado:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_certificado no puede estar vacío'
            }), 400)
        
        certificado = Certificado.query.filter_by(id_certificado=id_certificado).first()

        if not certificado:
            return make_response(jsonify({
                'status': 404,
                'message': 'Certificado no encontrado'
            }), 404)

        resultado = certificado_detalle_schema.dump(certificado)

        data = {
            "message": "Detalle del certificado obtenido correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:  
        print(f"Error en get_detalle_certificado: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# MARCAR CERTIFICADO COMO REVISADO
@certificado_routes.route('/marcar_certificado_revisado', methods=['POST'])
def marcar_certificado_revisado():
    try:
        # Validar que existe el JSON y los campos
        required_fields = ['id_certificado', 'id_usuario']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'id_certificado e id_usuario son requeridos'
            }), 400)
            
        id_certificado = request.json.get('id_certificado')
        id_usuario = request.json.get('id_usuario')

        # Validar que no sean None o vacíos
        if not id_certificado or not id_usuario:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_certificado e id_usuario no pueden estar vacíos'
            }), 400)
        
        certificado = Certificado.query.filter_by(id_certificado=id_certificado).first()

        if not certificado:
            return make_response(jsonify({
                'status': 404,
                'message': 'Certificado no encontrado'
            }), 404)

        # Verificar si ya está marcado como revisado
        if certificado.revisado:
            return make_response(jsonify({
                'status': 200,
                'message': 'El certificado ya estaba marcado como revisado'
            }), 200)

        # Actualizar y guardar
        certificado.revisado = True

        try:
            db.session.commit()
        except Exception as db_err:
            db.session.rollback()  # Revertir cambios en caso de error
            print(f"Error de base de datos: {db_err}")
            return make_response(jsonify({
                'status': 500,
                'message': 'Error al actualizar la base de datos'
            }), 500)
        
        # Llamar al servicio para que aumente puntos de experiencia al usuario
        servicio_experiencia = AUMENTAR_EXPERIENCIA

        respuesta_experiencia = request.post(servicio_experiencia, json={
            'id_usuario': id_usuario,
            'motivo': 2  # Motivo 2: Desbloqueo de certificado
        })

        if respuesta_experiencia.status_code != 200:
            return make_response(jsonify({
                'status': respuesta_experiencia.status_code,
                'message': 'Error aumentando experiencia con el servicio de usuario'
            }), respuesta_experiencia.status_code)
        
        # Respuesta exitosa, proceder a responder
        data = {
            "message": "Certificado marcado como revisado correctamente",
            "status": 200
        }

        return make_response(jsonify(data), 200)

    except Exception as err:  
        print(f"Error en marcar_certificado_revisado: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)