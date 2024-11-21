import re
from typing import Any, Dict

from utils.conversions import Conversions


class Buyer:
    def __init__(self, invoice: Dict[str, Any], addresses: list[Dict[str, Any]]):
        self.invoice = invoice
        self.addresses = addresses
        self.address_type = 1

    def manage_buyers(self, placeholder: str) -> str:
        normal_mapping = {
            '{{buyer_name}}': 'BUYER_NAME_0',
            '{{type_cod_buyer}}': 'TYPE_COD_REC_0',
            '{{type_cod_billTo}}': 'TYPE_COD_REC_0',
            '{{buyer_code}}': 'RECEIVER_COD_0',
            '{{billTo_code}}': 'RECEIVER_COD_0',
            '{{billTo_name}}': 'BUYER_NAME_0',
            '{{buyer_vat}}': 'BUYER_VAT_0',
            '{{billTo_vat}}': 'BUYER_VAT_0',
        }

        address_mapping = {
            '{{buyer_address}}': 'BPAADDLIG_0',
            '{{buyer_city}}': 'CTY_0',
            '{{buyer_country}}': 'CRY_0',
            '{{buyer_zip}}': 'POSCOD_0',
            '{{buyer_area}}': 'CTY_0',
            '{{buyer_phone}}': 'TEL_0',
            '{{buyer_email}}': 'WEB_0',
            '{{billTo_address}}': 'BPAADDLIG_0',
            '{{billTo_city}}': 'CTY_0',
            '{{billTo_country}}': 'CRY_0',
            '{{billTo_zip}}': 'POSCOD_0',
            '{{billTo_area}}': 'CTY_0',
            '{{billTo_phone}}': 'TEL_0',
            '{{billTo_email}}': 'WEB_0',
        }

        return_value = ''

        if placeholder in address_mapping:
            field_name = address_mapping.get(placeholder)

            for address in self.addresses:
                if address.get('BPATYP_0') == self.address_type:
                    return self.return_address_values(field_name, address)

        if placeholder in normal_mapping:
            field_name = normal_mapping.get(placeholder)

            return_value = Conversions.convert_value(self.invoice.get(field_name, ''), 0)

        return str(return_value)

    @staticmethod
    def return_address_values(field_name: str, address: Dict[str, Any]) -> str:
        return_value = ''

        if field_name == 'BPAADDLIG_0':
            return_value = ' '.join(
                address.get(f'BPAADDLIG_{i}', '').strip() for i in range(3)
            )
            poscod_field = address.get('POSCOD_0', '')
            return_value = f'{return_value.strip()}, {
                re.sub(r"(\d{4})(\d{3})", r"\1-\2", poscod_field)
            }'
        elif field_name == 'POSCOD_0' and address.get('CRY_0') == 'PT':
            return_value = re.sub(
                r'(\d{4})(\d{3})', r'\1-\2', address.get(field_name, '')
            )
        elif field_name in {'CTY_0', 'TEL_0', 'WEB_0', 'POSCOD_0'}:
            return_value = address.get(field_name, '')
        else:
            return_value = Conversions.convert_value(address.get(field_name, ''), 0)

        return str(return_value)
