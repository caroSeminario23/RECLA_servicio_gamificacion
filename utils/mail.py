from flask_mail import Mail

mail = Mail()

def init_mail(app):
    from config import (
        mail_server, mail_port, mail_use_tls,
        mail_username, mail_password, mail_default_sender
    )
    
    app.config['MAIL_SERVER'] = mail_server
    app.config['MAIL_PORT'] = int(mail_port)
    app.config['MAIL_USE_TLS'] = mail_use_tls
    app.config['MAIL_USERNAME'] = mail_username
    app.config['MAIL_PASSWORD'] = mail_password
    app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender
    
    mail.init_app(app)