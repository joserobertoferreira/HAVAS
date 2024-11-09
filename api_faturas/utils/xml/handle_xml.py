import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict


class HandleXML:
    def __init__(self, mapping_file_path: str, database_record: Dict[str, Any] = None):
        self.mapping = self.load_mapping(mapping_file_path)
        self.data_cache = database_record if database_record is not None else {}

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
            return field_name
            # data = self.fetch_data(table_name)
            # return data[field_name].iloc[0] if not data.empty else ''

        return placeholder

    def process_mapping_value(self, value: Any) -> Any:
        """Process a value from the mapping to replace placeholders."""
        if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
            return self.resolve_placeholder(value)
        elif isinstance(value, dict):
            return {k: self.process_mapping_value(v) for k, v in value.items()}
        return value

    def create_root_element(self):
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

    @staticmethod
    def create_sub_element(
        parent: ET.Element, tag: str, value: Dict[str, Any]
    ) -> ET.Element:
        """Create an XML sub-element with a tag and value."""
        return ET.SubElement(parent, tag, value)

    def create_sub_element_from_mapping(
        self, parent: ET.Element, tag: str, config: Any
    ) -> None:
        """Create an XML sub-element from a JSON mapping with placeholders."""

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
            condition_value = condition['value']

            # Check if the condition is met
            if condition_field == condition_value:
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
            condition_value = condition['value']

            # Check if the condition is met
            if condition_field == condition_value:
                # Define os atributos do elemento com base na configuração da condição
                attributes = self.process_mapping_value(condition['attributes'])
                element = ET.SubElement(parent, tag_name, attributes)
                element.text = default_value
                return

        # If the condition is not met, create the element without additional attributes
        element = ET.SubElement(parent, tag_name)
        element.text = default_value

    # Auxiliary function to add an element
    def add_element(self, parent, id_elem, atributes={}):
        id_config = self.mapping[id_elem]
        elem = ET.SubElement(parent, id_elem, atributes)

        return id_config, elem

    # Auxiliary function to add a party element
    def add_party_element(self, parent, party_type, atributes={}):
        party_id_config, party_elem = self.add_element(parent, party_type, atributes)

        if isinstance(party_id_config, dict):
            for key, value in party_id_config.items():
                self.create_sub_element_from_mapping(party_elem, key, value)
        else:
            party_elem.text = self.process_mapping_value(party_id_config)

    def add_element_test(self, parent, id_elem, id_sub_elem, atributes={}):
        id_config = self.mapping[id_elem][id_sub_elem]
        elem = ET.SubElement(parent, id_sub_elem, atributes)

        return id_config, elem

    # Auxiliary function to add a party element
    def add_party_element_test(self, parent, party_type, parent_party, atributes={}):
        party_id_config, party_elem = self.add_element_test(
            parent, parent_party, party_type, atributes
        )

        if isinstance(party_id_config, dict):
            for key, value in party_id_config.items():
                self.create_sub_element_from_mapping(party_elem, key, value)
        else:
            party_elem.text = self.process_mapping_value(party_id_config)

    def insert_element(
        self,
        parent: ET.Element,
        tag: str,
        conditional: bool = False,
        parent_tag: str = None,
    ) -> None:
        if conditional:
            self.add_conditional_element(parent, tag, self.mapping[tag])
        elif parent_tag:
            self.add_party_element_test(parent, tag, parent_tag)
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
                'documentNumber': self.mapping['invoice']['documentNumber'],
                'documentDate': self.mapping['invoice']['documentDate'],
                'schemaVersion': self.mapping['invoice']['schemaVersion'],
                'xmlns': 'urn:netdocs:schemas:document',
            },
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

        elements = [(invoice, 'currencyCode'), (invoice, 'discount')]
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
        line_item = self.create_sub_element(
            invoice, 'lineItem', {'number': self.mapping['lineItem']['number']}
        )

        elements = [
            (line_item, 'gtinCode'),
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
        vat_summary = self.create_sub_element(
            invoice,
            'vatSummary',
            self.add_conditional_sub_element(self.mapping['vatSummary']),
        )

        elements = [
            (vat_summary, 'vatPercentage', True),
            (vat_summary, 'vatAmount', False, 'vatSummary'),
            (vat_summary, 'taxableAmount', False, 'vatSummary'),
        ]
        for element in elements:
            self.insert_element(*element)

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
