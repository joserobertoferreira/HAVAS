from typing import Any, Dict

from utils.conversions import Conversions


class LineItems:
    def __init__(
        self,
        line_items: list[Dict[str, Any]],
        vat_summary: list[Dict[str, Any]],
    ):
        self.line_items = line_items
        self.vat_summary = vat_summary

    def manage_line_items(self, placeholder: str, tag: str, index_line: int) -> str:
        lines_mapping = {
            '{{line_unit_pr}}': 4,
            '{{line_vat_amt}}': 2,
            '{{line_net_amt}}': 2,
            '{{vat_amount}}': 2,
            '{{taxable_amt}}': 2,
        }

        # Get precision from the placeholder
        precision = lines_mapping.get(placeholder, 0)

        # Get the field name from the placeholder
        field_name = placeholder.replace('{{', '').replace('}}', '').upper() + '_0'

        if field_name:
            if tag == 'vatSummary':
                cache = self.vat_summary
            else:
                cache = self.line_items

            if cache:
                return_value = Conversions.convert_value(
                    cache[index_line][field_name], precision
                )

                return str(return_value)

        return ''
