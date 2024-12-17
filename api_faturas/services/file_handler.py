from typing import Any, Dict

from utils.handle_files import HandleFiles


class FileHandlerService:
    def __init__(self, base_dir: str, folder_in: str, folder_out: str):
        self.file_handler = HandleFiles(base_dir, folder_in, folder_out)

    def check_for_xml_files(self) -> list:
        return self.file_handler.check_for_xml_files()

    def generate_base64_strings(self, xml_list: list) -> dict:
        return self.file_handler.generate_base64_strings(xml_list)

    def move_file(self, file: str) -> None:
        self.file_handler.move_file(file)

    def create_message_files(self, messages: list[Dict[str, Any]]) -> None:
        self.file_handler.create_message_files(messages)

    def validate_xml(self, file: str) -> bool:
        return self.file_handler.validate_xml(file)

    def delete_file(
        self, work_path: str, file: str = '', delete_dir: bool = False
    ) -> bool:
        return self.file_handler.delete_file(work_path, file, delete_dir)
