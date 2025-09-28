from utils.ma import ma
from marshmallow import fields


class StickerDesbloqueadoConEstadoSchema(ma.Schema):
    class Meta:
        fields = (
            'id_sticker',
            'url_imagen',
            'precio',
            'categoria',
            'id_usuario',
            'desbloqueado'
        )
    
    id_sticker = fields.Integer()
    url_imagen = fields.String()
    precio = fields.Integer()
    categoria = fields.String()
    id_usuario = fields.Integer()
    desbloqueado = fields.Boolean()


# INSTANCIAS DE SCHEMAS
sticker_con_estado_schema = StickerDesbloqueadoConEstadoSchema()
stickers_con_estado_schema = StickerDesbloqueadoConEstadoSchema(many=True)