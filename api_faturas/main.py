from http import HTTPStatus

from auth.auth import Auth
from config import settings
from messages.messages import ProcessedMessages
from utils.handle_files import HandleFiles


def api_faturas() -> None:
    # Check if exists files to be processed
    fileHandler = HandleFiles(settings.FOLDER_XML_IN, settings.FOLDER_XML_OUT)

    xml_list = fileHandler.check_for_xml_files()

    if xml_list:
        # Generate the base64 strings
        base64_strings = fileHandler.generate_base64_strings(xml_list)

        if base64_strings:
            # Get the authentication token
            authentication = Auth.login(
                settings.SERVER_BASE_ADDRESS,
                settings.API_USER,
                settings.API_PASSWORD,
            )

            # # Check if the authentication was successful
            if authentication['HttpStatus'] == HTTPStatus.OK:
                handle_messages = ProcessedMessages(
                    settings.SERVER_BASE_ADDRESS,
                    authentication,
                )

                # Send the messages
                handle_messages.send_message(settings.SENDER, base64_strings)


if __name__ == '__main__':
    api_faturas()
