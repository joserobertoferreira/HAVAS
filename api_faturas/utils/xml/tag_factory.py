import xml.etree.ElementTree as ET
from typing import Any, Dict

from utils.comparisons import compare
from utils.handle_emails import HandleEmails


class TagFactory:
    def __init__(self):
        pass

    def process_mapping_value(self, value: Any, extra: str | None = None) -> Any:
        """Process a value from the mapping to replace placeholders."""
        if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
            return self.resolve_placeholder(value, extra)
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
        elif isinstance(config, dict) and tag != 'contactInformation':
            self.process_dict_config(parent, tag, config)
        elif isinstance(config, dict) and tag == 'contactInformation':
            self.process_contact_config(parent, tag, config)
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
                # Create a sub-element for other simple values
                elif self.is_special_case(tag, key):
                    text = self.process_mapping_value(value)

                    if len(text.strip()) > 0:
                        sub_elem = ET.SubElement(element, key)
                        sub_elem.text = text
                else:
                    sub_elem = ET.SubElement(element, key)
                    sub_elem.text = self.process_mapping_value(value)

    def process_contact_config(self, parent: ET.Element, tag: str, config: dict) -> None:
        """Process the case where config is a dictionary, handling attributes and
        sub-elements."""
        if parent.tag == 'seller':
            email_list = HandleEmails().extract_from_dict(self.addresses[0], 'WEB')
        else:
            email_list = HandleEmails().extract_from_dict(self.addresses[1], 'WEB')

        if len(email_list) == 0:
            self.process_dict_config(parent, tag, config)
        else:
            self.process_dict_contact(parent, tag, config, email_list)

    def process_dict_contact(
        self, parent: ET.Element, tag: str, config: dict, email_list: list
    ) -> None:
        # Create the XML sub-element
        for email in email_list:
            element = ET.SubElement(parent, tag)

            # Check and apply attributes if `attributes` key is present
            if 'attributes' in config and isinstance(config['attributes'], list):
                for attr_dict in config['attributes']:
                    if 'attribute' in attr_dict and 'attr_value' in attr_dict:
                        attribute_name = self.process_mapping_value(
                            attr_dict['attribute']
                        )
                        attribute_value = self.process_mapping_value(
                            attr_dict['attr_value']
                        )
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
                    # Create a sub-element for other simple values
                    elif self.is_special_case(tag, key):
                        text = self.process_mapping_value(value, email)

                        if len(text.strip()) > 0:
                            sub_elem = ET.SubElement(element, key)
                            sub_elem.text = text
                    else:
                        sub_elem = ET.SubElement(element, key)
                        sub_elem.text = self.process_mapping_value(value)

    @staticmethod
    def is_special_case(tag: str, key: str) -> bool:
        """Check if the tag and key combination is a special case."""
        return (
            (tag == 'contactInformation' and key in {'phone', 'email'})
            or (tag == 'addressInformation' and key == 'city')
            # or (tag == 'postalCode' and key in {'zip', 'area'})
        )

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

    def add_single_element(self, parent, party_type, **kwargs):
        arguments = {
            'id_elem': party_type,
            'id_sub_elem': kwargs.get('id_sub_elem', None),
            'atributes': kwargs.get('atributes', {}),
        }
        party_id_config, party_elem = self.add_element(parent, **arguments)

        party_elem.text = self.process_mapping_value(party_id_config)

        if party_type == 'vatPercentage':
            self.process_atributes(party_elem, party_type)

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

    def add_conditional_element(self) -> Dict[str, str]:
        if self.current_tag == 'vatSummary':
            return self.process_parent_atributes(self.current_tag)

        return {}

    # def add_conditional_element(self, parent, tag_name, config):
    # Define the default value of the element based on the configuration
    # default_value = self.process_mapping_value(config['default']['value'])

    # # Check if there is a condition in the configuration
    # if 'condition' in config:
    #     # Extract the field and value of the condition
    #     condition = config['condition']
    #     condition_field = self.resolve_placeholder(condition['field'])
    #     operator = condition['operator']
    #     condition_value = condition['value']

    #     # Check if the condition is met
    #     #            if condition_field == condition_value:
    #     if compare(operator, condition_field, condition_value):
    #         # Define os atributos do elemento com base na configuração da condição
    #         attributes = self.process_mapping_value(condition['attributes'])
    #         element = ET.SubElement(parent, tag_name, attributes)
    #         element.text = default_value
    #         return

    # # If the condition is not met, create the element without additional attributes
    # element = ET.SubElement(parent, tag_name)
    # element.text = default_value

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
