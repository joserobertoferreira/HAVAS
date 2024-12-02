import os

from utils.json.json_validator import JSONValidator
from utils.xml.xml_parser import XMLParser


class ValidationManager:
    def __init__(self, xml_file):
        self.xml_parser = XMLParser(xml_file)
        self.json_validator = JSONValidator()

    def run_validation(self):
        """
        Combine the XML and JSON validation process.
        """
        # Parse the XML
        self.xml_parser.parse()
        schema_locations = self.xml_parser.get_schema_locations()

        # Load the JSON files
        for schema in schema_locations:
            if os.path.exists(schema):
                self.json_validator.load_json(schema)
            else:
                print(f'Arquivo JSON não encontrado: {schema}')

        # Make the XML data available for the JSON validation
        xml_data = {elem.tag: elem.text for elem in self.xml_parser.root.iter()}
        results = self.json_validator.validate(xml_data)

        return results
