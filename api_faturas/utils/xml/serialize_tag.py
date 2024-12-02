from typing import Any, Dict

from utils.conversions import Conversions


class SerializeXML:
    def __init__(
        self,
        invoice: Dict[str, Any],
    ):
        self.invoice = invoice

    def return_base64_value(self, placeholder: str) -> str:
        """Return a generic value for the placeholder."""

        base64_mapping = {
            '{{attachment_base64}}': 'PDF_FILE_0',
        }

        field_name = base64_mapping.get(placeholder)

        if field_name:
            full_filename = self.invoice.get(field_name)
            return Conversions.convert_file_to_base64(
                file_path=full_filename.rpartition('\\')[0],
                file_name=full_filename.rpartition('\\')[-1],
            )

        return ''
