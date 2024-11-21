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
            '{{vat_Percentage}}': 0,
        }

        # Get precision from the placeholder
        precision = lines_mapping.get(placeholder, 0)

        # Get the field name from the placeholder
        field_name = placeholder.replace('{{', '').replace('}}', '').upper() + '_0'

        return_value = ''

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

        return return_value

    def add_atributes(self, element, tag: str, index_line: int) -> None:
        if tag == 'vatPercentage':
            return_value = self.manage_line_items('{{vat_rea_code}}', tag, index_line)

            if return_value:
                return_reason = self.manage_line_items('{{vat_reason}}', tag, index_line)

                element.set('vatExemptionReasonCode', return_value)
                element.set('vatExemptionReason', return_reason)
                element.set('xmlns', '')

    def add_parent_atributes(self, tag: str, index_line: int) -> Dict[str, str]:
        return_value = {}

        if tag in {'vatSummary'}:
            reason_code = self.manage_line_items('{{vat_rea_code}}', tag, index_line)

            if reason_code:
                return_value['exemptionReasonCode'] = reason_code
                return_value['exemptionReason'] = self.manage_line_items(
                    '{{vat_reason}}', tag, index_line
                )

            return_value['xmlns'] = ''

        return return_value
