from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
import requests

from utils.db import db
from utils.servicios_externos import AUMENTAR_EXPERIENCIA, OBTENER_CORREO_USUARIO
from functions.generar_certificado import generar_certificado_pdf
from functions.enviar_certificado import enviar_certificado_por_correo
from models.certificado import Certificado
from models.certificado_desbloqueado import CertificadoDesbloqueado
from schemas.certificado import certificado_detalle_schema
from schemas.certificado_desbloqueado import certificados_con_estado_schema

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
        
        consulta_certificados_con_estado = """
        SELECT 
            C.id_certificado, 
            C.nombre, 
            C.url_imagen, 
            C.nivel,
            CASE 
                WHEN CD.id_certificado IS NOT NULL 
                THEN true
                ELSE false
            END as desbloqueado,
            CASE
                WHEN CD.revisado IS NULL
                THEN false
                WHEN CD.revisado = false
                THEN false
                ELSE true
            END as revisado
        FROM certificado as C
        LEFT JOIN certificado_desbloqueado as CD 
            ON C.id_certificado = CD.id_certificado 
            AND CD.id_usuario = :id_usuario
        ORDER BY C.nivel, C.id_certificado;    
        """

        certificados_con_estado = db.session.execute(text(consulta_certificados_con_estado), {'id_usuario': id_usuario})

        resultado_raw = [dict(row._mapping) for row in certificados_con_estado]
        resultado = certificados_con_estado_schema.dump(resultado_raw)

        data = {
            'message': 'Certificados obtenidos exitosamente',
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
            
    except Exception as err:
        print(f"Error en get_certificados_con_estado: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)

    
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
        
        certificado_desbloqueado = CertificadoDesbloqueado.query.filter_by(
            id_certificado=id_certificado,
            id_usuario=id_usuario
        ).first()

        # Verificar si ya está marcado como revisado
        if certificado_desbloqueado.revisado:
            return make_response(jsonify({
                'status': 200,
                'message': 'El certificado ya estaba marcado como revisado'
            }), 200)

        # Actualizar y guardar
        certificado_desbloqueado.revisado = True

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

        respuesta_experiencia = requests.post(servicio_experiencia, json={
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


# ENVIAR CERTIFICADO POR CORREO
@certificado_routes.route('/enviar_certificado', methods=['POST'])
def enviar_certificado():
    try:
        # Validar que existe el JSON y los campos
        required_fields = ['id_certificado', 'id_usuario', 'username', 'plantilla_url']
        if not request.json or not all(field in request.json for field in required_fields):
            return make_response(jsonify({
                'status': 400,
                'message': 'id_certificado, id_usuario, username y plantilla_url son requeridos'
            }), 400)
        
        id_certificado = request.json.get('id_certificado')
        id_usuario = request.json.get('id_usuario')
        username = request.json.get('username')
        plantilla_url = request.json.get('plantilla_url')

        # Validar que no sean None o vacíos
        if not id_certificado or not id_usuario or not username or not plantilla_url:
            return make_response(jsonify({
                'status': 400,
                'message': 'id_certificado, id_usuario, username y plantilla_url no pueden estar vacíos'
            }), 400)
        
        # Verificar que el certificado esté desbloqueado para el usuario
        certificado_desbloqueado = CertificadoDesbloqueado.query.filter_by(
            id_certificado=id_certificado,
            id_usuario=id_usuario
        ).first()

        if not certificado_desbloqueado:
            return make_response(jsonify({
                'status': 404,
                'message': 'Certificado desbloqueado no encontrado para el usuario'
            }), 404)
        
        certificado_coordenadas = Certificado.query.filter_by(id_certificado=id_certificado).first().plantilla
        
        if not certificado_desbloqueado.pdf_url:
            generar_certificado_pdf(
                username=username,
                fecha_desbloqueo=certificado_desbloqueado.fec_desbloqueo,
                plantilla_url=plantilla_url,
                coordenadas=certificado_coordenadas,
                id_usuario=id_usuario,
                id_certificado=id_certificado
            )
        
        # Obtener el URL del PDF desde la base de datos
        pdf_url_certificado = CertificadoDesbloqueado.query.filter_by(
            id_certificado=id_certificado,
            id_usuario=id_usuario
        ).first().pdf_url

        if not pdf_url_certificado:
            return make_response(jsonify({
                'status': 404,
                'message': 'PDF del certificado no encontrado'
            }), 404)
        
        # Llamar al servicio para obtener la dirección de correo del usuario
        servicio_usuario = OBTENER_CORREO_USUARIO

        respuesta_usuario = requests.post(servicio_usuario, json={
            'id_usuario': id_usuario
        })

        if respuesta_usuario.status_code != 200:
            return make_response(jsonify({
                'status': respuesta_usuario.status_code,
                'message': 'Error obteniendo dirección de correo del usuario'
            }), respuesta_usuario.status_code)

        email_usuario = respuesta_usuario.json().get('data', {}).get('email')

        if not email_usuario:
            return make_response(jsonify({
                'status': 404,
                'message': 'Correo del usuario no encontrado'
            }), 404)

        enviar_certificado_por_correo(
            username=username,
            destinatario=email_usuario,
            pdf_url=pdf_url_certificado
        )

        # Añadir después de enviar el correo:
        return make_response(jsonify({
            'status': 200,
            'message': 'Certificado enviado exitosamente por correo'
        }), 200)

    except Exception as err:
        print(f"Error en enviar_certificado_pdf: {err}")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
   