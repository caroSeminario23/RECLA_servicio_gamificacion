import random

def generar_codigo_certificado():
    caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    codigo = ''.join(random.choices(caracteres, k=8))
    return codigo