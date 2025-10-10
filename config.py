from dotenv import load_dotenv
import os

load_dotenv()

# Cargar las variables de entorno desde el archivo .env
user = os.getenv('DB_USER')
pwd = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
db = os.getenv('DB_NAME')
server = os.getenv('DB_SERVER')
port = os.getenv('DB_PORT')

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

mail_server = os.getenv('MAIL_SERVER')
mail_port = os.getenv('MAIL_PORT')
mail_use_tls = os.getenv('MAIL_USE_TLS')
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
mail_default_sender = os.getenv('MAIL_DEFAULT_SENDER')


# Crear la cadena de conexión
DATABASE_CONNECTION = f'{server}://{user}:{pwd}@{host}:{port}/{db}'