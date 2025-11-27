from flask import Flask
from flask_cors import CORS
from flask_mail import Mail, Message
import os

from utils.db import db
from utils.mail import mail, init_mail
from config import DATABASE_CONNECTION
from services.insignia import insignia_routes
from services.certificado import certificado_routes
from services.sticker import sticker_routes
from services.recurso_educativo import recurso_educativo_routes

app = Flask(__name__)

init_mail(app)

CORS(
    app, 
    origins = "*", #dirección del front-end
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers = ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
    supports_credentials = True
)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION

db.init_app(app)

app.register_blueprint(insignia_routes, url_prefix='/insignia_routes')
app.register_blueprint(certificado_routes, url_prefix='/certificado_routes')
app.register_blueprint(sticker_routes, url_prefix='/sticker_routes')
app.register_blueprint(recurso_educativo_routes, url_prefix='/recurso_educativo_routes')

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', debug=True, port=port)
