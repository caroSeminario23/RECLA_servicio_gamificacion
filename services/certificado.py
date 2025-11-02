from flask import Blueprint, request, jsonify, make_response
from sqlalchemy import text
import requests, time
from concurrent.futures import ThreadPoolExecutor

from utils.db import db
from utils.logger import get_logger
from utils.servicios_externos import AUMENTAR_EXPERIENCIA, OBTENER_CORREO_USUARIO
from functions.generar_certificado import generar_certificado_pdf
from functions.enviar_certificado import enviar_certificado_por_correo
from models.certificado import Certificado
from models.certificado_desbloqueado import CertificadoDesbloqueado
from schemas.certificado import certificado_detalle_schema
from schemas.certificado_desbloqueado import (certificados_con_estado_schema, 
                                              certificados_desbloqueados_schema)


# Configurar el logger
logger = get_logger(__name__)

certificado_routes = Blueprint('certificado_routes', __name__)


# PRESENTACIÓN DE CERTIFICADOS (INDICANDO LOS DESBLOQUEADOS)
@certificado_routes.route('/get_certificados_con_estado', methods=['POST'])
def get_certificados_con_estado():
    inicio_tiempo = time.time()
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
            CD.desbloqueado,
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

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"get_certificados_con_estado exitoso para usuario {id_usuario}. Tiempo: {tiempo_respuesta:.2f}s")

        data = {
            'message': 'Certificados obtenidos exitosamente',
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
            
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_certificados_con_estado: {err}. Tiempo: {tiempo_respuesta:.2f}s")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)

    
# CONSULTAR DETALLE DE UN CERTIFICADO
@certificado_routes.route('/get_detalle_certificado', methods=['POST'])
def get_detalle_certificado():
    inicio_tiempo = time.time()
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

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"get_detalle_certificado exitoso para certificado {id_certificado}. Tiempo: {tiempo_respuesta:.2f}s")


        data = {
            "message": "Detalle del certificado obtenido correctamente",
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)

    except Exception as err:  
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_detalle_certificado: {err}. Tiempo: {tiempo_respuesta:.2f}s")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)
    

# AUMENTAR EXPERIENCIA AL USUARIO (POR DESBLOQUEO DE CERTIFICADO)
def _aumentar_experiencia_certificado(id_usuario):
    """Ejecuta en background sin bloquear la respuesta"""
    try:
        respuesta = requests.post(AUMENTAR_EXPERIENCIA, 
            json={'id_usuario': id_usuario, 'motivo': 2},
            timeout=3)
        if respuesta.status_code != 200:
            logger.error(f"Error aumentando experiencia: {respuesta.text}")
    except Exception as e:
        logger.error(f"Error en certificado background task: {e}")

# MARCAR CERTIFICADO COMO REVISADO
@certificado_routes.route('/marcar_certificado_revisado', methods=['POST'])
def marcar_certificado_revisado():
    inicio_tiempo = time.time()
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
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Certificado no encontrado: {id_certificado}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 404,
                'message': 'Certificado no encontrado'
            }), 404)
        
        '''
        certificado_desbloqueado = CertificadoDesbloqueado.query.filter_by(
            id_certificado=id_certificado,
            id_usuario=id_usuario
        ).first()
        '''

        certificado_desbloqueado = db.session.execute(text("""
            SELECT revisado
            FROM certificado_desbloqueado
            WHERE id_certificado = :id_certificado AND id_usuario = :id_usuario
        """), {'id_certificado': id_certificado, 'id_usuario': id_usuario}
        ).first()

        # Verificar si ya está marcado como revisado
        if certificado_desbloqueado.revisado:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.info(f"Certificado ya revisado para usuario {id_usuario}, certificado {id_certificado}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 200,
                'message': 'El certificado ya estaba marcado como revisado'
            }), 200)

        try:
            # Actualizar y guardar
            query_update = text(f"""
                UPDATE certificado_desbloqueado
                SET revisado = TRUE
                WHERE id_certificado=id_certificado AND id_usuario=id_usuario
            """)
            db.session.execute(query_update, {
                'id_certificado': id_certificado,
                'id_usuario': id_usuario
            })
            db.session.commit()
            #certificado_desbloqueado.revisado = True
        except Exception as db_err:
            db.session.rollback()  # Revertir cambios en caso de error
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error de base de datos en marcar_certificado_revisado: {db_err}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 500,
                'message': 'Error al actualizar la base de datos'
            }), 500)
        
        logger.info(f"Aumentando experiencia para usuario {id_usuario}")
        
        # ⭐ Ejecutar experiencia en background (NO bloquea)
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(_aumentar_experiencia_certificado, id_usuario)
        
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"marcar_certificado_revisado exitoso para usuario {id_usuario} y certificado {id_certificado}. Tiempo: {tiempo_respuesta:.2f}s")

        # Respuesta exitosa, proceder a responder
        data = {
            "message": "Certificado marcado como revisado correctamente",
            "status": 200
        }

        return make_response(jsonify(data), 200)

    except Exception as err:  
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en marcar_certificado_revisado: {err}. Tiempo: {tiempo_respuesta:.2f}s")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)


# ENVIAR CERTIFICADO POR CORREO
@certificado_routes.route('/enviar_certificado', methods=['POST'])
def enviar_certificado():
    inicio_tiempo = time.time()
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
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error en enviar_certificado: Certificado desbloqueado no encontrado para el usuario {id_usuario}, certificado {id_certificado}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 404,
                'message': 'Certificado desbloqueado no encontrado para el usuario'
            }), 404)
        
        certificado_coordenadas = Certificado.query.filter_by(id_certificado=id_certificado).first().plantilla
        
        if not certificado_desbloqueado.pdf_url:
            logger.info(f"Generando PDF para usuario {id_usuario}, certificado {id_certificado}")
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
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"PDF del certificado no encontrado para usuario {id_usuario}, certificado {id_certificado}. Tiempo: {tiempo_respuesta:.2f}s")
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
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Error obteniendo correo del usuario {id_usuario}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': respuesta_usuario.status_code,
                'message': 'Error obteniendo dirección de correo del usuario'
            }), respuesta_usuario.status_code)

        email_usuario = respuesta_usuario.json().get('data', {}).get('email')

        if not email_usuario:
            tiempo_respuesta = time.time() - inicio_tiempo
            logger.error(f"Correo del usuario no encontrado. Usuario: {id_usuario}. Tiempo: {tiempo_respuesta:.2f}s")
            return make_response(jsonify({
                'status': 404,
                'message': 'Correo del usuario no encontrado'
            }), 404)

        logger.info(f"Enviando certificado a {email_usuario} para usuario {id_usuario}")
        enviar_certificado_por_correo(
            username=username,
            destinatario=email_usuario,
            pdf_url=pdf_url_certificado
        )

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"enviar_certificado exitoso para usuario {id_usuario}, email: {email_usuario}. Tiempo: {tiempo_respuesta:.2f}s")

        # Añadir después de enviar el correo:
        return make_response(jsonify({
            'status': 200,
            'message': 'Certificado enviado exitosamente por correo'
        }), 200)

    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en enviar_certificado_pdf: {err}. Tiempo: {tiempo_respuesta:.2f}s")  # Para debugging
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)


# PRESENTACIÓN DE CERTIFICADOS DE UN USUARIO (SOLO LAS DESBLOQUEADAS)
@certificado_routes.route('/get_certificados_desbloqueados_usuario', methods=['POST'])
def get_certificados_desbloqueados_usuario():
    inicio_tiempo = time.time()
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
        
        consulta_certificados_desbloqueadas = """
        SELECT 
            C.id_certificado, 
            C.nombre, 
            C.url_imagen, 
            C.nivel
        FROM certificado as C
        RIGHT JOIN certificado_desbloqueado as CD 
            ON C.id_certificado = CD.id_certificado 
            AND CD.id_usuario = :id_usuario
        ORDER BY C.nivel, C.id_certificado;   
        """

        certificados_desbloqueados = db.session.execute(text(consulta_certificados_desbloqueadas), {'id_usuario': id_usuario})

        resultado_raw = [dict(row._mapping) for row in certificados_desbloqueados]
        resultado = certificados_desbloqueados_schema.dump(resultado_raw)

        tiempo_respuesta = time.time() - inicio_tiempo
        logger.info(f"get_certificados_desbloqueados_usuario exitoso para usuario {id_usuario}. Tiempo: {tiempo_respuesta:.2f}s")

        data = {
            'message': 'Certificados obtenidos exitosamente',
            "status": 200,
            "data": resultado
        }

        return make_response(jsonify(data), 200)
            
    except Exception as err:
        tiempo_respuesta = time.time() - inicio_tiempo
        logger.error(f"Error en get_certificados_desbloqueados_usuario: {err}. Tiempo: {tiempo_respuesta:.2f}s")
        return make_response(jsonify({
            'status': 500,
            'message': 'Error procesando la solicitud'
        }), 500)