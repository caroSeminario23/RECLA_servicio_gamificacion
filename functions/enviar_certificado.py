from flask_mail import Message
from utils.mail import mail

def enviar_certificado_por_correo(username, destinatario, pdf_url):
    try:
        asunto = "RECLA - Certificado emitido"
        cuerpo = f"Felicidades {username}, tu certificado ha sido emitido. Puedes descargarlo aquí: {pdf_url}"
        
        msg = Message(subject=asunto, recipients=[destinatario])
        msg.body = cuerpo
        mail.send(msg)
        print("Certificado enviado exitosamente.")
        return True
    
    except Exception as e:
        print(f"Error al enviar el certificado: {e}")
        return False