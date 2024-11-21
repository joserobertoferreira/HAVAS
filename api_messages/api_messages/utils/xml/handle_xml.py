from pathlib import Path

import xmltodict


class HandleXML:
    def __init__(self, folder_input: str = '', folder_output: str = ''):
        self.folder_input = folder_input
        self.folder_output = folder_output

    def convert_xml_to_dict(self, xml: str) -> dict:
        xml_file = Path(self.folder_input / xml)

        xml_dict = {}

        with open(xml_file, 'rb') as file:
            xml_dict = xmltodict.parse(file.read())

        return xml_dict
