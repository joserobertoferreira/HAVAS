import base64
from datetime import datetime
from pathlib import Path


class HandleFiles:
    def __init__(self, folder_input: str, folder_output: str):
        self.folder_input = folder_input
        self.folder_output = folder_output

    def check_for_xml_files(self) -> list[str]:
        work_path = Path(self.folder_input)

        # Check if the folder exists
        if not work_path.is_dir():
            work_path.mkdir(parents=True, exist_ok=True)

        # List all files in the folder
        xml_files = list(file.name for file in work_path.glob('*.xml'))

        # Return the list of XML files or a message if none are found
        return xml_files

    def generate_base64_strings(self, xml_list: list[str]) -> dict[str, str]:
        base64_strings = {}

        for xml_file in xml_list:
            file_attributes = Path(self.folder_input) / xml_file

            # Open the file in binary mode and read its content
            with file_attributes.open('rb') as file:
                content = file.read()
                base_string = base64.b64encode(content).decode('utf-8')
                base64_strings[file_attributes.stem] = base_string

        return base64_strings

    def move_file(self, file: str) -> None:
        # Get the full path of the file to move
        file_to_move = Path(self.folder_input) / file

        # Create the output folder with the current year and month
        year_month_folder = datetime.now().strftime('%Y%m')
        output_path = Path(self.folder_output) / year_month_folder

        # Check if the folder exists
        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        # Move the file to the output folder
        file_to_move.replace(Path(output_path) / file)
