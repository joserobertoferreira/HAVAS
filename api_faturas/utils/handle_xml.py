import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any


class HandleXML:
    def __init__(self, mapping_file_path: str):
        self.mapping = self.load_mapping(mapping_file_path)
        self.data_cache = {}

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

    def resolve_placeholder(self, placeholder: str) -> str:
        """Substitute placeholders with the corresponding value from the database
        or the current date.
        """
        # Placeholder actions that do not require a database query
        placeholder_actions = {
            '{{creation_date_time}}': self.get_current_date_time,
            '{{data_atual}}': self.get_current_date,
        }

        if placeholder in placeholder_actions:
            return placeholder_actions[placeholder]()

        match = re.match(r'\{\{(\w+)\.(\w+)\}\}', placeholder)
        if match:
            table_name, field_name = match.groups()
            data = self.fetch_data(table_name)
            return data[field_name].iloc[0] if not data.empty else ''

        return placeholder

    def process_mapping_value(self, value: Any) -> Any:
        """Process a value from the mapping to replace placeholders."""
        if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
            return self.resolve_placeholder(value)
        elif isinstance(value, dict):
            return {k: self.process_mapping_value(v) for k, v in value.items()}
        return value

    def add_conditional_element(self, parent, tag_name, config):
        """Add a conditional XML tag based on a configuration with conditions."""
        default_value = self.process_mapping_value(config['default']['value'])

        if 'condition' in config:
            condition = config['condition']
            condition_field = self.resolve_placeholder(condition['field'])
            condition_value = condition['value']

            if condition_field == condition_value:
                attributes = self.process_mapping_value(condition['attributes'])
                element = ET.SubElement(parent, tag_name, attributes)
                element.text = default_value
                return

        # If the condition is not met, create the element without additional attributes
        element = ET.SubElement(parent, tag_name)
        element.text = default_value

    def generate_xml(self, output_file):  # noqa: PLR0914
        """Generate the XML file based on the provided mapping."""

        def create_root_element():
            """Create the root <message> element with namespaces and attributes."""
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

        def create_invoice_element(parent):
            """Create the <invoice> sub element with namespaces and attributes."""
            return ET.SubElement(
                parent,
                'invoice',
                {
                    'documentNumber': self.mapping['invoice']['documentNumber'],
                    'documentDate': self.mapping['invoice']['documentDate'],
                    'schemaVersion': self.mapping['invoice']['schemaVersion'],
                    'xmlns': 'urn:netdocs:schemas:document',
                },
            )

        # Auxiliary function to add a party element
        def add_party_element(parent, party_type, atributes={}):
            party_elem = ET.SubElement(parent, party_type, atributes)

            party_id_config = self.mapping[party_type]['id']
            party_id_elem = ET.SubElement(party_elem, 'id')
            party_id_elem.set(
                party_id_config['attribute'],
                self.process_mapping_value(party_id_config['attr_value']),
            )
            party_id_elem.text = self.process_mapping_value(party_id_config['value'])

            return party_elem

        def add_sub_party_element(elem, party, party_type, party_elem=[]):
            party_info_config = self.mapping[party][party_type]
            party_info_elem = ET.SubElement(elem, party_type)

            if party_elem:
                for element in party_elem:
                    if isinstance(element, list):
                        code_elem = ET.SubElement(party_info_elem, element[0])
                        for tag in element[1:]:
                            tag_elem = ET.SubElement(code_elem, tag)
                            tag_elem.text = (
                                self.process_mapping_value(party_info_config[tag]),
                            )
                    else:
                        code_elem = ET.SubElement(party_info_elem, element)
                        code_elem.text = self.process_mapping_value(
                            party_info_config[element]
                        )
            else:
                party_info_elem.text = self.process_mapping_value(party_info_config)

        # Create the root element
        root = create_root_element()

        # Add the <sender> element
        sender = add_party_element(root, 'sender', {'xmlns': ''})
        add_sub_party_element(sender, 'sender', 'addressInformation', ['countryCode'])

        # Add the <receiver> element
        receiver = add_party_element(root, 'receiver', {'xmlns': ''})
        add_sub_party_element(
            receiver, 'receiver', 'addressInformation', ['countryCode']
        )

        # Add the <invoice> element
        invoice = create_invoice_element(root)

        # Add the <seller> element
        seller = add_party_element(invoice, 'seller', {'xmlns': ''})
        add_sub_party_element(seller, 'seller', 'name')
        add_sub_party_element(
            seller,
            'seller',
            'addressInformation',
            ['address', 'city', ['postalCode', 'zip', 'area'], 'countryCode'],
        )

        # self.add_conditional_element(
        #     invoice_elem, 'vatPercentage', self.mapping['lineItem']['vatPercentage']
        # )

        # Save the XML to a file
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"Arquivo XML '{output_file}' gerado com sucesso.")
