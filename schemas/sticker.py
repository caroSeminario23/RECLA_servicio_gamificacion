from utils.ma import ma
#from marshmallow import fields

from models.sticker import Sticker

# SCHEMAS
class StickerConsultaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sticker
        fields = (
            'id_sticker',
            'url_imagen',
            'precio'
        )

# INSTANCIAS DE SCHEMAS
sticker_consulta_schema = StickerConsultaSchema()
stickers_consulta_schema = StickerConsultaSchema(many=True)