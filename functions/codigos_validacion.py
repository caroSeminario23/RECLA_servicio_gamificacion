from models.certificado_desbloqueado import CertificadoDesbloqueado
from schemas.certificado_desbloqueado import certificados_cod_validacion_schema

def obtener_codigos_validacion():
    certificados_desbloqueados = CertificadoDesbloqueado.query.filter(
        CertificadoDesbloqueado.cod_validacion.isnot(None)
    ).all()
    
    cods_validacion = certificados_cod_validacion_schema.dump(certificados_desbloqueados)

    # Convertirlos en un arreglo de strings
    codigos = [item['cod_validacion'] for item in cods_validacion if 'cod_validacion' in item]
    
    return codigos