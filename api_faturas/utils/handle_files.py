import base64
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class HandleFiles:
    def __init__(self, base_folder: str, folder_input: str, folder_output: str):
        self.base_folder = base_folder
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

    @staticmethod
    def list_folder(path_folder: str) -> list[dict[str, str]]:
        """
        Lists the contents of the folder and identifies the extension and Content-Type
         of each file.

        Args:
            path_folder: str) -> list[dict[str, str]]: (str or Path): Path to the folder
            to be read.

        Returns:
            list: List of dictionaries containing 'filename', 'extension' and
            'content_type'.
        """
        folder_content = []

        # Convert the path to a Path object, if it is not already
        path = Path(path_folder)

        # Check if the path is a valid folder
        if not path.is_dir():
            return folder_content

        # Iterates over the folder content
        for item in path.iterdir():
            # Only processes if it is a file
            if item.is_file():
                # Define the Content-Type using the file extension
                content_type, _ = mimetypes.guess_type(item)

                # Add the result to the list
                folder_content.append({
                    'file_name': item.stem,
                    'suffix': item.suffix,
                    'content_type': content_type if content_type else 'unknown',
                })

        return folder_content

    def create_message_files(self, messages: list[Dict[str, Any]]) -> None:
        # Create the output folder with the current year and month
        year_month_folder = datetime.now().strftime('%Y%m')
        output_path = Path(self.folder_output) / year_month_folder

        # Check if the folder exists
        if not output_path.is_dir():
            output_path.mkdir(parents=True, exist_ok=True)

        for message in messages:
            # Create a file with the message content
            try:
                file_name = message['ResultData']['Filename']
                base64_data = message['ResultData']['Base64Data']
                content_type = message['ResultData']['ContentType']

                suffix = mimetypes.guess_extension(content_type) or '.bin'

                file_data = base64.b64decode(base64_data)
                file_path = output_path / f'{file_name}{suffix}'

                with file_path.open('wb') as file:
                    file.write(file_data)

            except KeyError as e:
                print(f'Missing key {e} in dictionary: {message}')
            except base64.binascii.Error:
                print(f'Invalid Base64 content in file {file_name}.')
            except Exception as e:
                print(f'An error occurred while processing {file_name}: {e}')
