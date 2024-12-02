import xml.etree.ElementTree as ET


class XMLParser:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = None
        self.root = None

    def parse(self):
        """Execute the parsing of the XML file."""
        self.tree = ET.parse(self.xml_file)
        self.root = self.tree.getroot()

    def get_schema_locations(self):
        """
        Return the values of @schemalocation in the xsd:include and xsd:import keys.
        """
        if self.root is None:
            raise ValueError("XML não foi parseado. Chame o método 'parse' antes.")

        schema_locations = []

        # Search for xsd:include or xsd:import in the tree
        for elem in self.root.findall('.//{*}include') + self.root.findall(
            './/{*}import'
        ):
            schemalocation = elem.attrib.get('schemalocation')
            if schemalocation:
                schema_locations.append(schemalocation)

        return schema_locations
