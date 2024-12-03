import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict


class XSDParser:
    def __init__(self, file_paths: list[str | Path]) -> None:
        """
        Initialize the class with the paths to the XSD files.

        Args:
            file_paths list[(str | Path)]: List of paths to the XSD files.
        """
        self.file_paths = file_paths

    def extract_patterns(self) -> Dict[str, str]:
        """
        Extract the patterns from the XSD files.

        Returns:
            Dict[str, str]: Dictionary with the patterns extracted from the XSD files.
        """
        patterns = {}
        namespace = {'xs': 'http://www.w3.org/2001/XMLSchema'}

        for file_path in self.file_paths:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Seek for the simple types with restrictions
            for simple_type in root.findall('.//xs:simpleType', namespace):
                type_name = simple_type.attrib.get('name')
                pattern_elem = simple_type.find('.//xs:pattern', namespace)

                if type_name and pattern_elem is not None:
                    patterns[type_name] = pattern_elem.attrib.get('value')

        return patterns
