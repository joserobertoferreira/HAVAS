from typing import Any, Dict

from config import settings
from utils.conversions import Conversions


class SerializeXML:
    def __init__(
        self,
        invoice: Dict[str, Any],
    ):
        self.invoice = invoice

    @staticmethod
    def return_base64_value(placeholder: str) -> str:
        """Return a generic value for the placeholder."""

        base64_mapping = {
            '{{attachment_base64}}': 'PDF_FILE_0',
        }

        field_name = base64_mapping.get(placeholder)

        if field_name:
            #            file_attributes = Path(self.data_cache.get(field_name))
            return Conversions.convert_file_to_base64(
                settings.FOLDER_XML_IN, 'FT-0132400008.pdf'
            )
            # file_attributes = Path(settings.FOLDER_XML_IN / 'FT-0132400008.pdf')

            # # Open the file in binary mode and read its content
            # with file_attributes.open('rb') as file:
            #     content = file.read()
            #     base_string = base64.b64encode(content).decode('utf-8')
            #     return base_string

        return ''
