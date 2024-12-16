import json

from lxml import etree

from config.settings import BASE_DIR
from utils.xml.validator import ValidatorData

HEADER_VALIDATORS = [
    'message',
    'invoice',
    'additionalDate',
    'reference',
    'currencyCode',
    'discount',
    'comment',
    'senderSoftwareCertificationNumber',
    'senderSoftwareDocumentSignatureHash',
    'atCud',
    'qrData',
    'lineItem',
    'vatSummary',
]
DETAIL_VALIDATORS = [
    'sender',
    'receiver',
    'seller',
    'buyer',
    'billTo',
    'qrText',
    'qrImage',
    'sellerItemCode',
    'description',
    'quantity',
    'freeQuantity',
    'netUnitPrice',
    'vatPercentage',
    'vatAmount',
    'taxableAmount',
]


class ValidateXML:
    def __init__(self, xml_file: str, validator_file: str, validator_enum: str):
        self.xml_file = BASE_DIR / 'uploads' / xml_file
        self.validator_file = self.load_json(validator_file)
        self.validator_enum = self.load_json(validator_enum)
        self.header_validators = HEADER_VALIDATORS
        self.detail_validators = DETAIL_VALIDATORS
        self.validator = ValidatorData()

    @staticmethod
    def load_json(json_file: str) -> dict:
        """Load the JSON file."""
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def remove_namespace(doc):
        for el in doc.getiterator():
            if not isinstance(el.tag, str):
                continue
            el.tag = el.tag.split('}', 1)[-1]  # Remove the namespace
        return doc

    def parse_xml(self):
        """Parse the XML file and return the root element."""
        try:
            tree = etree.parse(self.xml_file)
            tree = self.remove_namespace(tree)
            return tree
        except etree.XMLSyntaxError as e:
            raise ValueError(f'Erro ao analisar o XML: {e}')

    @staticmethod
    def validate_xml(results: dict) -> dict:
        for _, result in results.items():
            if isinstance(result, dict):
                for _, value in result.items():
                    if value.get('status') == 'error':
                        return value

        return {'status': 'success', 'message': 'Tag validada com sucesso.'}

    def process_xml(self) -> bool:
        """
        Process the XML and validate it against the JSON rules.
        """
        # Delete the previous errors from the database
        self.validator.delete_previous_errors(self.xml_file)

        try:
            root = self.parse_xml()
        except ValueError as error:
            # update the process with the error
            self.validator.update_database(self.xml_file, None, 'XML', error)
            return False

        return_process = True

        for node in root.iter():
            match node.tag:
                case el if el in self.header_validators:
                    header = self.validator_file.get(node.tag, {})
                    schema = header
                    process = node.tag
                    processed_tags = []
                    validation_results = {}
                case el if el in self.detail_validators:
                    detail = header.get(node.tag, {})
                    schema = detail
                    process = node.tag
                    processed_tags = []
                    validation_results = {}
                case _:
                    if node.tag in processed_tags:
                        continue

                    schema = detail.get(node.tag, {})

                    if node.getchildren():
                        self.process_node(
                            node,
                            schema,
                            process,
                            processed_tags,
                            validation_results,
                        )
                        if validation_results:
                            results = self.validate_xml(validation_results)

                            if (
                                results['status'] is not None
                                and results['status'] == 'error'
                            ):
                                return_process = False
                                parent_process = node.getparent().getparent().tag
                                # update the process with the error
                                self.validator.update_database(
                                    self.xml_file,
                                    parent_process,
                                    process,
                                    results['message'],
                                )

                        continue

            if schema:
                validation_results = self.validate_node(
                    node, schema, process, validation_results
                )
                if not validation_results:
                    continue

            results = self.validate_xml(validation_results)

            if results['status'] is not None and results['status'] == 'error':
                return_process = False
                parent_process = node.getparent().getparent().tag
                # update the process with the error
                self.validator.update_database(
                    self.xml_file, parent_process, process, results['message']
                )

        return return_process

    def process_node(
        self, node, schema, process: str, processed_tags: list, validation_results: dict
    ):
        for child in node.iterchildren():
            processed_tags.append(child.tag)
            validation_results = self.validate_node(
                child, schema, process, validation_results
            )

            if child.getchildren():
                _schema = schema.get(child.tag, {})
                self.process_node(
                    child, _schema, process, processed_tags, validation_results
                )

        return validation_results

    def validate_node(self, node, schema, process: str, validation_results: dict):
        attribute_matches = self.validate_attributes(node, schema)
        if attribute_matches:
            if process not in validation_results:
                validation_results[process] = attribute_matches
            else:
                validation_results[process].update(attribute_matches)

        values_matches = self.validate_values(node, schema)
        if values_matches:
            if process not in validation_results:
                validation_results[process] = values_matches
            else:
                validation_results[process].update(values_matches)

        return validation_results

    def validate_values(self, node, schema):
        values_matches = {}
        if node.text:
            json_value = schema.get('value', {})
            if not json_value:
                json_value = schema.get(node.tag, {})
                if not json_value:
                    json_value = schema

            if json_value:
                return_validation = self.validator.execute_validation(
                    node.text, json_value, self.validator_enum
                )
                if return_validation:
                    values_matches['value'] = return_validation

        return values_matches

    def validate_attributes(self, node, schema):
        attributes = node.attrib
        attribute_matches = {}
        if attributes:
            for attr_name, attr_value in attributes.items():
                for json_attr in schema.get('attributes', []):
                    if attr_name in json_attr:
                        return_validation = self.validator.execute_validation(
                            attr_value, json_attr[attr_name], self.validator_enum
                        )
                        attribute_matches[attr_name] = return_validation
        return attribute_matches

    def open_json_file(self, tag: str) -> dict:
        validator_file = {}

        json_file = self.json_path / f'{tag}_validation.json'

        validator_file = self.load_json(json_file)

        return validator_file
