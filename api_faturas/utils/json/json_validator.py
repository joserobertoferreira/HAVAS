import json


class JSONValidator:
    def __init__(self):
        self.validation_rules = {}

    def load_json(self, json_file):
        """
        Load a JSON file and store its rules.
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.validation_rules[json_file] = data

    def validate(self, xml_data):
        """
        Validate the XML data based on the loaded rules.
        """
        validation_results = {}

        for json_file, rules in self.validation_rules.items():
            # Validation logic based on the JSON content
            for key, expected_value in rules.items():
                actual_value = xml_data.get(key)
                validation_results[key] = actual_value == expected_value

        return validation_results
