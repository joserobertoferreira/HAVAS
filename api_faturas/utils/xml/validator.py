import xml.etree.ElementTree as ET


class ValidatorXML:
    def __init__(self) -> None:
        pass

    @staticmethod
    def validate(xml_file: str, xsd_file: str) -> bool:
        try:
            xml = ET.parse(xml_file)
            xsd = ET.parse(xsd_file)

            schema = XMLSchema(xsd)
            schema.validate(xml)

            return True
        except Exception as e:
            print(e)

            return False
