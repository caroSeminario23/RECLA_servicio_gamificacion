from flask_mail import Message
from utils.mail import mail

def enviar_certificado_por_correo(username, destinatario, certificado_url):
    try:
        asunto = "RECLA - Certificado emitido"
        #cuerpo = f"Felicidades {username}, tu certificado ha sido emitido. Puedes descargarlo aquí: {certificado_url}"
        
        cuerpo_html = f"""
        <html>
            <body>
                <p>Felicidades <strong>{username}</strong>, tu certificado ha sido emitido.</p>
                <br>
                <img src="{certificado_url}" alt="Certificado" style="max-width: 600px; height: auto;">
                <br>
                <p>Recuerda que puedes descargarlo haciendo click <a href="{certificado_url}">aquí</a>.</p>
            </body>
        </html>
        """

        msg = Message(subject=asunto, recipients=[destinatario])
        msg.html = cuerpo_html
        mail.send(msg)
        print("Certificado enviado exitosamente.")
        return True
    
    except Exception as e:
        print(f"Error al enviar el certificado: {e}")
        return False