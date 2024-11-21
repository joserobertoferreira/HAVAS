import base64
from typing import Any, Dict

# from utils.conversions import Conversions


class QRCode:
    def __init__(self, qr_codes: list[Dict[str, Any]]):
        self.qr_codes = qr_codes

    def manage_qr_code(self, placeholder: str) -> str:
        qr_code_mapping = {
            '{{software_certification_number}}': 'QRC_R_0',
            '{{software_document_signature_hash}}': 'QRC_Q_0',
            '{{at_cud}}': 'QRC_H_0',
            '{{qr_text}}': 'STRQRC_0',
            '{{qr_image_name}}': 'DOCNUM_0',
            '{{qr_image_base64}}': 'IMGQRC_0',
        }

        field_name = qr_code_mapping.get(placeholder)

        if field_name:
            for qrcode in self.qr_codes:
                if field_name in qrcode:
                    if field_name == 'IMGQRC_0':
                        return base64.b64encode(qrcode[field_name]).decode('utf-8')
                    else:
                        return str(qrcode[field_name])

        return ''
