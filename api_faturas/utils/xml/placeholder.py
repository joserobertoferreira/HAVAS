from datetime import datetime, timezone
from typing import Dict

from utils.conversions import Conversions
from utils.xml.buyer_tag import Buyer
from utils.xml.line_items_tag import LineItems
from utils.xml.qr_code_tag import QRCode
from utils.xml.seller_tag import Seller
from utils.xml.serialize_tag import SerializeXML

NORMAL = 1
WITH_TIME = 2


class Placeholder:
    def __init__(self, **kwargs) -> None:
        self.field_headers = kwargs.get('field_headers', [])  # list[str]
        self.data_cache = kwargs.get('db_record', {})  # Dict[str, Any]
        self.addresses = kwargs.get('db_addresses', [{}])  # list[Dict[str, Any]]
        self.qrcode_cache = kwargs.get('db_qrcode', [{}])  # list[Dict[str, Any]]
        self.lines_cache = kwargs.get('db_lines', [{}])  # list[Dict[str, Any]]
        self.vat_summary_cache = kwargs.get('db_vat_summary', [{}])  # list[Dict]]

        self.line_number = 0
        self.current_tag = ''
        self.parent_tag = ''
        self.cache = {}

    @staticmethod
    def get_current_date_time() -> str:
        """Get the current date and time in ISO format."""
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace('+00:00', '.000')
        )

    @staticmethod
    def get_current_date() -> str:
        """Get the current date."""
        return datetime.now(timezone.utc).strftime('%Y-%m-%d')

    def format_datetime(self, placeholder: str, conversion_type: int) -> str:
        """Format a datetime object to a string."""
        field_name = placeholder.replace('{{', '').replace('}}', '').upper() + '_0'

        if conversion_type == NORMAL:
            return_date = self.data_cache.get(field_name, '').strftime('%Y-%m-%d')
        elif conversion_type == WITH_TIME:
            return_date = (
                self.data_cache.get(field_name, '').strftime('%Y-%m-%dT%H:%M:%S') + '.000'
            )

        return return_date

    def resolve_placeholder(self, placeholder: str, extra: str | None = None) -> str:
        """Substitute placeholders with the corresponding value from the database
        or the current date.
        """

        # Deal with the specific placeholders
        return_value = self.resolve_specific_placeholder(placeholder, extra)

        if return_value:
            return return_value

        # Placeholder actions thats require another approach
        placeholder_actions = {
            '{{creation_date_time}}': self.get_current_date_time,
            '{{data_atual}}': self.get_current_date,
            '{{invoice_date}}': lambda: self.format_datetime(placeholder, NORMAL),
            '{{additionaldt}}': lambda: self.format_datetime(placeholder, WITH_TIME),
        }

        return_value = None

        if placeholder in placeholder_actions:
            return_value = placeholder_actions[placeholder]()

        if return_value is not None:
            return return_value

        # Get the field name from the placeholder
        field_name = placeholder.replace('{{', '').replace('}}', '').upper() + '_0'

        # Check if the field name is in the field headers
        if field_name in self.field_headers:
            if field_name in {
                'TOT_VAT_AMT_0',
                'TOT_TAX_AMT_0',
                'TOTAL_AMOUNT_0',
            }:
                return_value = Conversions.convert_value(
                    self.data_cache.get(field_name, ''), 2
                )
            else:
                return_value = Conversions.convert_value(
                    self.data_cache.get(field_name, ''), 0
                )
            return str(return_value)

        return str(placeholder)

    def resolve_specific_placeholder(
        self, placeholder: str, extra: str | None = None
    ) -> str:
        # Deal with the seller tag
        if self.parent_tag == 'seller':
            if 'seller' not in self.cache:
                self.cache['seller'] = Seller(self.data_cache, self.addresses)
            seller = self.cache['seller']
            return seller.manage_sellers(placeholder)

        # Deal with the buyer and billTo tags
        if self.parent_tag in {'buyer', 'billTo'}:
            if 'buyer' not in self.cache:
                self.cache['buyer'] = Buyer(self.data_cache, self.addresses)
            buyer = self.cache['buyer']
            return buyer.manage_buyers(placeholder, extra)

        # Deal with the QR Code tag
        if self.parent_tag == 'qrData':
            if 'qr_code' not in self.cache:
                self.cache['qr_code'] = QRCode(self.qrcode_cache)
            qr_code = self.cache['qr_code']
            return qr_code.manage_qr_code(placeholder)

        # Deal with the line items and vat summary tags
        if self.parent_tag == 'lineItem':
            if 'line_items' not in self.cache:
                self.cache['line_items'] = LineItems(
                    self.lines_cache,
                    self.vat_summary_cache,
                )
            line_items = self.cache['line_items']
            return line_items.manage_line_items(
                placeholder, self.current_tag, self.line_number
            )

        # Deal with serialize items
        if self.parent_tag == 'base64Attachment':
            if 'base64' not in self.cache:
                self.cache['base64'] = SerializeXML(self.data_cache)
            base64 = self.cache['base64']
            return base64.return_base64_value(placeholder)

        return ''

    def process_atributes(self, element, tag: str) -> None:
        """Process the attributes of the tag."""
        if tag in {'vatPercentage'}:
            if 'line_items' not in self.cache:
                self.cache['line_items'] = LineItems(
                    self.lines_cache,
                    self.vat_summary_cache,
                )
            line_items = self.cache['line_items']
            line_items.add_atributes(element, tag, self.line_number)

    def process_parent_atributes(self, tag: str) -> Dict[str, str]:
        """Process the attributes of the parent tag."""
        if tag in {'vatSummary'}:
            if 'line_items' not in self.cache:
                self.cache['line_items'] = LineItems(
                    self.lines_cache,
                    self.vat_summary_cache,
                )
            line_items = self.cache['line_items']
            return line_items.add_parent_atributes(tag, self.line_number)

        return {}
