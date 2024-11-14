import base64
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict

from config import settings
from utils.comparisons import compare
from utils.conversions import Conversions
from utils.handle_files import HandleFiles

NORMAL = 1
WITH_TIME = 2
ATTACH_PDF = 2


class HandleXML:  # noqa: PLR0904
    def __init__(self, **kwargs) -> None:
        self.mapping = self.load_mapping(kwargs.get('mapping_file_path'))
        self.field_headers = kwargs.get('field_headers', [])  # list[str]
        self.data_cache = kwargs.get('db_record', {})  # Dict[str, Any]
        self.qrcode_cache = kwargs.get('db_qrcode', [{}])  # list[Dict[str, Any]]
        self.lines_cache = kwargs.get('db_lines', [{}])  # list[Dict[str, Any]]
        self.vat_summary_cache = kwargs.get(
            'db_vat_summary', [{}]
        )  # list[Dict[str, Any]]
        self.addresses = kwargs.get('db_addresses', [{}])  # list[Dict[str, Any]]
        self.line_number = 0
        self.current_tag = ''

    def load_mapping(self, file_path: str) -> Any:  # noqa: PLR6301
        """Load a JSON mapping from a file.

        Args:
            file_path (str): The path to the file containing the mapping.

        Returns:
            JSON dict: The mapping loaded from the file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

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

    def return_address_value(self, placeholder: str, address_type: int) -> str:
        """Return a generic value for the placeholder."""

        address_mapping = {
            '{{seller_address}}': 'BPAADDLIG_0',
            '{{buyer_address}}': 'BPAADDLIG_0',
            '{{billTo_address}}': 'BPAADDLIG_0',
        }

        complement_mapping = {
            '{{seller_city}}': 'CTY_0',
            '{{seller_country}}': 'CRY_0',
            '{{seller_zip}}': 'POSCOD_0',
            '{{seller_area}}': 'CTY_0',
            '{{seller_phone}}': 'TEL_0',
            '{{seller_location}}': 'CTY_0',
            '{{buyer_city}}': 'CTY_0',
            '{{buyer_country}}': 'CRY_0',
            '{{buyer_zip}}': 'POSCOD_0',
            '{{buyer_area}}': 'CTY_0',
            '{{buyer_phone}}': 'TEL_0',
            '{{buyer_email}}': 'WEB_0',
            '{{billTo_city}}': 'CTY_0',
            '{{billTo_country}}': 'CRY_0',
            '{{billTo_zip}}': 'POSCOD_0',
            '{{billTo_area}}': 'CTY_0',
            '{{billTo_phone}}': 'TEL_0',
            '{{billTo_email}}': 'WEB_0',
        }

        for address in self.addresses:
            if address.get('BPATYP_0') == address_type:
                if placeholder in address_mapping:
                    return_value = ' '.join(
                        address.get(f'BPAADDLIG_{i}', '').strip() for i in range(3)
                    )
                    return_value = return_value.strip()
                elif placeholder in complement_mapping:
                    field_name = complement_mapping.get(
                        placeholder,
                        placeholder.replace('{{', '').replace('}}', '').upper() + '_0',
                    )

                    if field_name == 'POSCOD_0' and address.get('CRY_0') == 'PT':
                        return_value = re.sub(
                            r'(\d{4})(\d{3})', r'\1-\2', address.get(field_name, '')
                        )
                    else:
                        return_value = Conversions.convert_value(
                            address.get(field_name, ''), 0
                        )

                return str(return_value)

        return ''

    def return_normal_value(self, placeholder: str) -> str:
        """Return a generic value for the placeholder."""

        normal_mapping = {
            '{{buyer_code}}': 'RECEIVER_COD_0',
            '{{billTo_code}}': 'RECEIVER_COD_0',
            '{{type_cod_buyer}}': 'TYPE_COD_REC_0',
            '{{type_cod_billTo}}': 'TYPE_COD_REC_0',
            '{{billTo_name}}': 'BUYER_NAME_0',
            '{{seller_vat}}': 'SELLER_COMM_0',
            '{{billTo_vat}}': 'BUYER_VAT_0',
        }

        field_name = normal_mapping.get(
            placeholder,
            placeholder.replace('{{', '').replace('}}', '').upper() + '_0',
        )
        return_value = Conversions.convert_value(self.data_cache.get(field_name, ''), 0)

        return str(return_value)

    def return_line_value(self, placeholder: str, precision: int) -> str:
        """Return a generic value for the placeholder."""

        line_mapping = {}

        # Get the field name from the placeholder
        field_name = line_mapping.get(
            placeholder,
            placeholder.replace('{{', '').replace('}}', '').upper() + '_0',
        )

        if field_name:
            if self.current_tag == 'vatSummary':
                cache = self.vat_summary_cache
            else:
                cache = self.lines_cache

            if cache:
                return_value = Conversions.convert_value(
                    cache[self.line_number][field_name], precision
                )

                return str(return_value)

        return ''

    def return_qr_code_value(self, placeholder: str) -> str:
        """Return a generic value for the placeholder."""

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
            for qrcode in self.qrcode_cache:
                if field_name in qrcode:
                    if field_name == 'IMGQRC_0':
                        return base64.b64encode(qrcode[field_name]).decode('utf-8')
                    else:
                        return str(qrcode[field_name])

        return ''

    def return_base64_value(self, placeholder: str) -> str:  # noqa: PLR6301
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

    def resolve_placeholder(self, placeholder: str) -> str:
        """Substitute placeholders with the corresponding value from the database
        or the current date.
        """
        # Placeholder actions thats require another approach
        placeholder_actions = {
            '{{creation_date_time}}': self.get_current_date_time,
            '{{data_atual}}': self.get_current_date,
            '{{invoice_date}}': lambda: self.format_datetime(placeholder, NORMAL),
            '{{additionaldt}}': lambda: self.format_datetime(placeholder, WITH_TIME),
        }

        normal_placeholders = {
            '{{seller_vat}}': lambda: self.return_normal_value(placeholder),
            '{{type_cod_buyer}}': lambda: self.return_normal_value(placeholder),
            '{{buyer_code}}': lambda: self.return_normal_value(placeholder),
            '{{type_cod_billTo}}': lambda: self.return_normal_value(placeholder),
            '{{billTo_code}}': lambda: self.return_normal_value(placeholder),
            '{{billTo_name}}': lambda: self.return_normal_value(placeholder),
            '{{billTo_vat}}': lambda: self.return_normal_value(placeholder),
        }

        address_placeholders = {
            '{{seller_address}}': lambda: self.return_address_value(placeholder, 3),
            '{{seller_city}}': lambda: self.return_address_value(placeholder, 3),
            '{{seller_zip}}': lambda: self.return_address_value(placeholder, 3),
            '{{seller_area}}': lambda: self.return_address_value(placeholder, 3),
            '{{seller_country}}': lambda: self.return_address_value(placeholder, 3),
            '{{seller_phone}}': lambda: self.return_address_value(placeholder, 3),
            '{{seller_location}}': lambda: self.return_address_value(placeholder, 3),
            '{{buyer_address}}': lambda: self.return_address_value(placeholder, 1),
            '{{buyer_city}}': lambda: self.return_address_value(placeholder, 1),
            '{{buyer_zip}}': lambda: self.return_address_value(placeholder, 1),
            '{{buyer_area}}': lambda: self.return_address_value(placeholder, 1),
            '{{buyer_country}}': lambda: self.return_address_value(placeholder, 1),
            '{{buyer_phone}}': lambda: self.return_address_value(placeholder, 1),
            '{{buyer_email}}': lambda: self.return_address_value(placeholder, 1),
            '{{billTo_address}}': lambda: self.return_address_value(placeholder, 1),
            '{{billTo_city}}': lambda: self.return_address_value(placeholder, 1),
            '{{billTo_zip}}': lambda: self.return_address_value(placeholder, 1),
            '{{billTo_area}}': lambda: self.return_address_value(placeholder, 1),
            '{{billTo_country}}': lambda: self.return_address_value(placeholder, 1),
            '{{billTo_phone}}': lambda: self.return_address_value(placeholder, 1),
            '{{billTo_email}}': lambda: self.return_address_value(placeholder, 1),
        }

        qr_code_placeholders = {
            '{{software_certification_number}}': lambda: self.return_qr_code_value(
                placeholder
            ),
            '{{software_document_signature_hash}}': lambda: self.return_qr_code_value(
                placeholder
            ),
            '{{at_cud}}': lambda: self.return_qr_code_value(placeholder),
            '{{qr_text}}': lambda: self.return_qr_code_value(placeholder),
            '{{qr_image_name}}': lambda: self.return_qr_code_value(placeholder),
            '{{qr_image_base64}}': lambda: self.return_qr_code_value(placeholder),
        }

        lines_placeholders = {
            '{{line_number}}': lambda: self.return_line_value(placeholder, 0),
            '{{line_product}}': lambda: self.return_line_value(placeholder, 0),
            '{{line_descr}}': lambda: self.return_line_value(placeholder, 0),
            '{{line_quant}}': lambda: self.return_line_value(placeholder, 0),
            '{{line_unit}}': lambda: self.return_line_value(placeholder, 0),
            '{{line_unit_pr}}': lambda: self.return_line_value(placeholder, 4),
            '{{line_vat_amt}}': lambda: self.return_line_value(placeholder, 2),
            '{{line_net_amt}}': lambda: self.return_line_value(placeholder, 2),
            '{{vat_percent}}': lambda: self.return_line_value(placeholder, 0),
            '{{vat_rea_code}}': lambda: self.return_line_value(placeholder, 0),
            '{{vat_reason}}': lambda: self.return_line_value(placeholder, 0),
        }

        vat_summary_placeholders = {
            '{{vat_amount}}': lambda: self.return_line_value(placeholder, 2),
            '{{taxable_amt}}': lambda: self.return_line_value(placeholder, 2),
        }

        base64_placeholders = {
            '{{attachment_base64}}': lambda: self.return_base64_value(placeholder),
        }

        return_value = None

        if placeholder in placeholder_actions:
            return_value = placeholder_actions[placeholder]()

        if placeholder in normal_placeholders:
            return_value = normal_placeholders[placeholder]()

        if placeholder in address_placeholders:
            return_value = address_placeholders[placeholder]()

        if placeholder in qr_code_placeholders:
            return_value = qr_code_placeholders[placeholder]()

        if placeholder in lines_placeholders:
            return_value = lines_placeholders[placeholder]()

        if placeholder in vat_summary_placeholders:
            return_value = vat_summary_placeholders[placeholder]()

        if placeholder in base64_placeholders:
            return_value = base64_placeholders[placeholder]()

        if return_value is not None:
            return return_value

        # Get the field name from the placeholder
        field_name = placeholder.replace('{{', '').replace('}}', '').upper() + '_0'

        # Check if the field name is in the field headers
        if field_name in self.field_headers:
            if field_name in {
                'SELL_SOCCAP_0',
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

    def process_mapping_value(self, value: Any) -> Any:
        """Process a value from the mapping to replace placeholders."""
        if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
            return self.resolve_placeholder(value)
        elif isinstance(value, dict):
            return {k: self.process_mapping_value(v) for k, v in value.items()}
        return value

    def create_root_element(self):
        """Create the root <message> element with namespaces and attributes."""
        self.current_tag = 'message'

        return ET.Element(
            'message',
            {
                'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
                'id': self.process_mapping_value(self.mapping['message']['id']),
                'creationDateTime': self.process_mapping_value(
                    self.mapping['message']['creationDateTime']
                ),
                'xmlns': 'urn:netdocs:schemas:message',
            },
        )

    def create_sub_element(
        self, parent: ET.Element, tag: str, value: Dict[str, Any]
    ) -> ET.Element:
        """Create an XML sub-element with a tag and value."""
        self.current_tag = tag

        return ET.SubElement(parent, tag, value)

    def create_sub_element_from_mapping(
        self, parent: ET.Element, tag: str, config: Any
    ) -> None:
        """Create an XML sub-element from a JSON mapping with placeholders."""

        self.current_tag = tag

        # Determine how to process the config based on its type
        if isinstance(config, list):
            self.process_list_config(parent, tag, config)
        elif isinstance(config, dict):
            self.process_dict_config(parent, tag, config)
        else:
            # If not a dictionary, treat as a direct value of the element
            self.process_direct_value(parent, tag, config)

    def process_list_config(self, parent: ET.Element, tag: str, config: list) -> None:
        """Process the case where config is a list, creating attributes or elements."""
        # If tag is 'attributes', apply directly to parent; else create a sub-element
        element = parent if tag == 'attributes' else ET.SubElement(parent, tag)

        # Apply each dictionary in the list as an attribute
        for attr_dict in config:
            if 'attribute' in attr_dict and 'attr_value' in attr_dict:
                attribute_name = self.process_mapping_value(attr_dict['attribute'])
                attribute_value = self.process_mapping_value(attr_dict['attr_value'])
                element.set(attribute_name, attribute_value)

    def process_dict_config(self, parent: ET.Element, tag: str, config: dict) -> None:
        """Process the case where config is a dictionary, handling attributes and
        sub-elements."""

        # Create the XML sub-element
        element = ET.SubElement(parent, tag)

        # Check and apply attributes if `attributes` key is present
        if 'attributes' in config and isinstance(config['attributes'], list):
            for attr_dict in config['attributes']:
                if 'attribute' in attr_dict and 'attr_value' in attr_dict:
                    attribute_name = self.process_mapping_value(attr_dict['attribute'])
                    attribute_value = self.process_mapping_value(attr_dict['attr_value'])
                    element.set(attribute_name, attribute_value)

        # Define the element text if the `value` key is present
        if 'value' in config:
            element.text = self.process_mapping_value(config['value'])

        # Process other keys, creating sub-elements as needed
        for key, value in config.items():
            if key not in {'attributes', 'value'}:
                if isinstance(value, dict):
                    # Recursively handle nested dictionaries
                    self.create_sub_element_from_mapping(element, key, value)
                else:
                    # Create a sub-element for other simple values
                    sub_elem = ET.SubElement(element, key)
                    sub_elem.text = self.process_mapping_value(value)

    def process_direct_value(self, parent: ET.Element, tag: str, config: Any) -> None:
        """Process the case where config is a direct value, creating a simple element."""
        element = ET.SubElement(parent, tag)
        element.text = self.process_mapping_value(config)

    def add_conditional_sub_element(self, config):
        # Define the default value of the element based on the configuration
        default_value = self.process_mapping_value(config['default']['value'])  # noqa: F841

        # Check if there is a condition in the configuration
        if 'condition' in config:
            # Extract the field and value of the condition
            condition = config['condition']
            condition_field = self.resolve_placeholder(condition['field'])
            operator = condition['operator']
            condition_value = condition['value']

            # Check if the condition is met
            #            if condition_field == condition_value:
            if compare(operator, condition_field, condition_value):
                # Define os atributos do elemento com base na configuração da condição
                attributes = self.process_mapping_value(condition['attributes'])
                return attributes

        return {}

    def add_conditional_element(self, parent, tag_name, config):
        """Add a conditional XML tag based on a configuration with conditions."""

        # Define the default value of the element based on the configuration
        default_value = self.process_mapping_value(config['default']['value'])

        # Check if there is a condition in the configuration
        if 'condition' in config:
            # Extract the field and value of the condition
            condition = config['condition']
            condition_field = self.resolve_placeholder(condition['field'])
            operator = condition['operator']
            condition_value = condition['value']

            # Check if the condition is met
            #            if condition_field == condition_value:
            if compare(operator, condition_field, condition_value):
                # Define os atributos do elemento com base na configuração da condição
                attributes = self.process_mapping_value(condition['attributes'])
                element = ET.SubElement(parent, tag_name, attributes)
                element.text = default_value
                return

        # If the condition is not met, create the element without additional attributes
        element = ET.SubElement(parent, tag_name)
        element.text = default_value

    # Auxiliary function to add an element
    def add_element(self, parent, **kwargs):
        id_elem = kwargs.get('id_elem')
        id_sub_elem = kwargs.get('id_sub_elem', None)
        atributes = kwargs.get('atributes', {})

        if id_sub_elem is not None:
            id_config = self.mapping[id_sub_elem][id_elem]
        else:
            id_config = self.mapping[id_elem]

        elem = ET.SubElement(parent, id_elem, atributes)

        return id_config, elem

    # Auxiliary function to add a party element
    def add_party_element(self, parent, party_type, **kwargs):
        arguments = {
            'id_elem': party_type,
            'id_sub_elem': kwargs.get('id_sub_elem', None),
            'atributes': kwargs.get('atributes', {}),
        }
        party_id_config, party_elem = self.add_element(parent, **arguments)

        if isinstance(party_id_config, dict):
            for key, value in party_id_config.items():
                self.create_sub_element_from_mapping(party_elem, key, value)
        else:
            party_elem.text = self.process_mapping_value(party_id_config)

    # Auxiliary function to add a Saphety element
    def add_saphety_element(self, parent, saphety_type):
        saphety_id_config = self.mapping[saphety_type]
        saphety_elem = ET.SubElement(parent, saphety_type)

        for key, value in saphety_id_config.items():
            self.create_sub_element_from_mapping(saphety_elem, key, value)

    def insert_element(
        self,
        parent: ET.Element,
        tag: str,
        conditional: bool = False,
        parent_tag: str = None,
        saphety_tag: bool = False,
    ) -> None:
        if conditional:
            self.add_conditional_element(parent, tag, self.mapping[tag])
        elif parent_tag:
            self.add_party_element(parent, tag, id_sub_elem=parent_tag)
        elif saphety_tag:
            self.add_saphety_element(parent, tag)
        else:
            self.add_party_element(parent, tag)

    def generate_xml(self, output_file: str):
        """Generate the XML file based on the provided mapping."""

        # Create the root element
        root = self.create_root_element()

        # Add <sender>,<receiver> tags to element root
        elements = [(root, 'sender'), (root, 'receiver')]
        for element in elements:
            self.insert_element(*element)

        # Add the <invoice> element
        invoice = self.create_sub_element(
            root,
            'invoice',
            {
                'documentNumber': self.process_mapping_value(
                    self.mapping['invoice']['documentNumber']
                ),
                'documentDate': self.process_mapping_value(
                    self.mapping['invoice']['documentDate']
                ),
                'schemaVersion': self.mapping['invoice']['schemaVersion'],
                'xmlns': 'urn:netdocs:schemas:document',
            },
        )

        # Check if is necessary to add <binaryDocumentAttachment> element
        attach_pdf = self.data_cache.get('SEND_METHOD_0')

        if attach_pdf == ATTACH_PDF:
            binary_document = self.create_sub_element(
                invoice,
                'binaryDocumentAttachment',
                {
                    'name': self.process_mapping_value(
                        self.mapping['binaryDocumentAttachment']['name']
                    ),
                    'contentType': self.mapping['binaryDocumentAttachment'][
                        'contentType'
                    ],
                },
            )
            binary_document.text = self.process_mapping_value(
                self.mapping['binaryDocumentAttachment']['content']
            )

        attachments = HandleFiles.list_folder(settings.FOLDER_XML_IN / 'attachments')
        # attachments = HandleFiles.list_folder(self.data_cache.get('ATT_PATH_0'))

        if attachments:
            for attachment in attachments:
                binary_document = self.create_sub_element(
                    invoice,
                    'binaryDocumentAttachment',
                    {
                        'name': attachment.get('file_name'),
                        'contentType': attachment.get('content_type'),
                    },
                )
                binary_document.text = Conversions.convert_file_to_base64(
                    settings.FOLDER_XML_IN / 'attachments',
                    f'{attachment.get("file_name")}{attachment.get("suffix")}',
                )

        # Add the <seller>, <buyer>, and <billTo> elements to element invoice
        elements = [(invoice, 'seller'), (invoice, 'buyer'), (invoice, 'billTo')]
        for element in elements:
            self.insert_element(*element)

        # Begin of the specific information for Saphety
        # Add the <additionalDate> element inside the <invoice> element
        additional_date = self.create_sub_element(
            invoice,
            'additionalDate',
            {'type': self.mapping['additionalDate']['type']},
        )
        additional_date.text = self.process_mapping_value(
            self.mapping['additionalDate']['value']
        )

        # Add the <reference> element inside the <invoice> element when the
        # condition is met
        cost_center = self.data_cache.get('COST_CENTER_0', '')

        if len(cost_center) > 0:
            self.create_sub_element(
                invoice,
                'reference',
                {'type': 'COSTCENTER', 'referencedDocument': cost_center},
            )

        order = self.data_cache.get('REF_ORDER_0', '')

        if len(order) > 0:
            self.create_sub_element(
                invoice,
                'reference',
                {'type': 'ORDER', 'referencedDocument': order},
            )

        elements = [
            (invoice, 'currencyCode'),
            (invoice, 'discount'),
        ]
        for element in elements:
            self.insert_element(*element)

        # Add the <comment> element inside the <invoice> element
        comment = self.create_sub_element(
            invoice,
            'comment',
            {'id': self.mapping['comment']['id']},
        )
        comment.text = self.process_mapping_value(self.mapping['comment']['value'])
        # End of the specific information for Saphety

        elements = [
            (invoice, 'senderSoftwareCertificationNumber'),
            (invoice, 'senderSoftwareDocumentSignatureHash'),
            (invoice, 'atCud'),
            (invoice, 'qrData'),
        ]
        for element in elements:
            self.insert_element(*element)

        # Add the <lineItem> element to the invoice element
        for index_line, _ in enumerate(self.lines_cache):
            self.line_number = index_line
            self.current_tag = 'lineItem'

            line_item = self.create_sub_element(
                invoice,
                'lineItem',
                {
                    'number': self.process_mapping_value(
                        self.mapping['lineItem']['number']
                    )
                },
            )

            elements = [
                (line_item, 'sellerItemCode'),
                (line_item, 'description'),
                (line_item, 'quantity'),
                (line_item, 'freeQuantity'),
                (line_item, 'unitPrice'),
                (line_item, 'vatPercentage', True),
                (line_item, 'vatAmount'),
                (line_item, 'netAmount'),
            ]
            for element in elements:
                self.insert_element(*element)

        # Add the <vatSummary> element to the invoice element
        for index_line, _ in enumerate(self.vat_summary_cache):
            self.line_number = index_line
            self.current_tag = 'vatSummary'

            vat_summary = self.create_sub_element(
                invoice,
                'vatSummary',
                self.add_conditional_sub_element(self.mapping['vatSummary']),
            )

            elements = [
                (vat_summary, 'vatPercentage', False, 'vatSummary'),
                (vat_summary, 'vatAmount', False, 'vatSummary'),
                (vat_summary, 'taxableAmount', False, 'vatSummary'),
            ]
            for element in elements:
                self.insert_element(*element)

        # Add the final elements to the invoice element
        elements = [
            (invoice, 'totalVatAmount'),
            (invoice, 'totalTaxableAmount'),
            (invoice, 'totalNetAmount'),
            (invoice, 'totalPayableAmount'),
        ]
        for element in elements:
            self.insert_element(*element)

        # Save the XML to a file
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"Arquivo XML '{output_file}' gerado com sucesso.")
