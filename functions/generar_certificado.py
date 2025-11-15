from flask import jsonify, make_response
from PIL import Image, ImageDraw, ImageFont
from utils.supabase_client import supabase
import io, os, requests

from utils.db import db
from utils.generar_codigo import generar_codigo_certificado
from functions.codigos_validacion import obtener_codigos_validacion
from models.certificado_desbloqueado import CertificadoDesbloqueado

def generar_certificado_webp(username, fecha_desbloqueo, plantilla_url, coordenadas, id_usuario, id_certificado):
    # Extraer la plantilla desde Supabase
    imagen_plantilla = requests.get(plantilla_url)
    if imagen_plantilla.status_code != 200:
        return make_response(jsonify({
            'status': 500,
            'message': 'Error al obtener la plantilla desde Supabase'
        }), 500)

    imagen_editable = Image.open(io.BytesIO(imagen_plantilla.content))
    draw = ImageDraw.Draw(imagen_editable)

    # Cargar fuente
    font_path = os.path.join(os.path.dirname(__file__), "../fonts/ShareTechMono-Regular.ttf")
    font = ImageFont.truetype(font_path, size=24)

    # Coordenadas de datos dinámicos
    username_x = coordenadas.get("ecoaprendiz", {}).get("x", 100)
    username_y = coordenadas.get("ecoaprendiz", {}).get("y", 100)
    codigo_x = coordenadas.get("codigo", {}).get("x", 100)
    codigo_y = coordenadas.get("codigo", {}).get("y", 200)
    fec_desbloqueo_x = coordenadas.get("fecha", {}).get("x", 100)
    fec_desbloqueo_y = coordenadas.get("fecha", {}).get("y", 300)

    #username_x, username_y, codigo_x, codigo_y, fec_desbloqueo_x, fec_desbloqueo_y = map(int, str(coordenadas).split(','))

    # Obtener todos los códigos de validación existentes
    codigos_existentes = obtener_codigos_validacion()


    # Generar código de 8 dígitos único
    codigo = generar_codigo_certificado()
    while codigo in codigos_existentes:
        codigo = generar_codigo_certificado()

    # Escribir texto en la imagen
    draw.text((username_x, username_y), f"Usuario: {username}", fill="black", font=font)
    draw.text((fec_desbloqueo_x, fec_desbloqueo_y), f"Fecha de Desbloqueo: {fecha_desbloqueo}", fill="black", font=font)
    draw.text((codigo_x, codigo_y), f"Código: {codigo}", fill="black", font=font)
    
    # Guardar la imagen modificada como webp
    webp_output = f"certificado_{username}_{codigo}.webp"
    imagen_editable.save(webp_output, "WEBP", resolution=100.0)

    # Subir el WEBP a Supabase
    try:
        certificado_subido_url = subir_webp_a_supabase(webp_output)
    except Exception as e:
        print(f"Error al subir WEBP: {e}")
        return None

    # Guardar URL del WEBP en la base de datos
    almacenar_certificado_en_bd(id_usuario, id_certificado, certificado_subido_url, codigo)

    # Eliminar el archivo WEBP local después de subirlo
    os.remove(webp_output)
    

def subir_webp_a_supabase(webp_archivo):
    with open(webp_archivo, "rb") as webp_file:
        bucket_name = "recla-images"
        carpeta_supabase = f"certificados_generados/{webp_archivo}"

        llamado_carpeta = supabase.storage.from_(bucket_name)

        llamado_carpeta.upload(carpeta_supabase, webp_file, {'cacheControl': '3600', 'upsert': 'true'})
    webp_url = llamado_carpeta.get_public_url(f"certificados_generados/{webp_archivo}")
    print(f"WEBP subido a Supabase: {webp_url}")

    return webp_url


def almacenar_certificado_en_bd(id_usuario, id_certificado, webp_url, codigo):
    certificado_desbloqueado = CertificadoDesbloqueado.query.filter_by(id_usuario=id_usuario, id_certificado=id_certificado).first()

    if certificado_desbloqueado != None:
        certificado_desbloqueado.pdf_url = webp_url
        certificado_desbloqueado.cod_validacion = codigo
        db.session.commit()