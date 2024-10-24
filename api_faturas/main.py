from http import HTTPStatus

from auth.auth import Auth
from config import settings
from messages.messages import ProcessedMessages
from utils.handle_files import HandleFiles


def api_faturas() -> None:
    # Check if exists files to be processed
    fileHandler = HandleFiles(settings.FOLDER_XML_IN, settings.FOLDER_XML_OUT)

    xml_list = fileHandler.check_for_xml_files()

    if xml_list is None:
        print('No files to be processed.')

        return

    # Generate the base64 strings
    base64_strings = fileHandler.generate_base64_strings(xml_list)

    if base64_strings:
        for file, fileBase64 in base64_strings.items():
            # Get the authentication token
            authentication = Auth(settings.SERVER_BASE_ADDRESS)

            login = authentication.login(
                settings.API_USER,
                settings.API_PASSWORD,
            )

            # Check if the authentication was successful
            if login['HttpStatus'] == HTTPStatus.OK:
                handle_messages = ProcessedMessages(
                    settings.SERVER_BASE_ADDRESS,
                    login,
                )

                # Send the messages
                sent_message = handle_messages.send_message(
                    settings.SENDER, file, fileBase64
                )

                # Logout from API
                authentication.logout(login['Token'])

                # If the message was sent, move the file to the output folder
                if sent_message:
                    fileHandler.move_file(f'{file}.xml')


if __name__ == '__main__':
    api_faturas()
