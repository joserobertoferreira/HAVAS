import re
from typing import Any, Dict

from utils.conversions import Conversions


class Seller:
    def __init__(self, invoice: Dict[str, Any], addresses: list[Dict[str, Any]]):
        self.invoice = invoice
        self.addresses = addresses
        self.address_type = 3

    def manage_sellers(self, placeholder: str) -> str:
        normal_mapping = {
            '{{type_cod_sel}}': 'TYPE_COD_SEL_0',
            '{{seller_code}}': 'SELLER_CODE_0',
            '{{seller_name}}': 'SELLER_NAME_0',
            '{{seller_vat}}': 'SELLER_COMM_0',
            '{{seller_comm}}': 'SELLER_COMM_0',
            '{{sell_soccap}}': 'SELL_SOCCAP_0',
        }

        address_mapping = {
            '{{seller_address}}': 'BPAADDLIG_0',
            '{{seller_city}}': 'CTY_0',
            '{{seller_country}}': 'CRY_0',
            '{{seller_zip}}': 'POSCOD_0',
            '{{seller_area}}': 'CTY_0',
            '{{seller_phone}}': 'TEL_0',
            '{{seller_location}}': 'CTY_0',
        }

        return_value = ''

        if placeholder in address_mapping:
            for address in self.addresses:
                field_name = address_mapping.get(placeholder)

                if address.get('BPATYP_0') == self.address_type:
                    return self.return_address_values(field_name, address)

        if placeholder in normal_mapping:
            field_name = normal_mapping.get(placeholder)

            if field_name == 'SELL_SOCCAP_0':
                return_value = Conversions.convert_value(
                    self.invoice.get(field_name, ''), 2
                )
            else:
                return_value = Conversions.convert_value(
                    self.invoice.get(field_name, ''), 0
                )

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
