from http import HTTPStatus

from auth.auth import Auth
from config import settings
from database.database import DatabaseConnection
from messages.messages import ProcessedMessages
from utils.handle_files import HandleFiles


def api_faturas() -> None:
    with DatabaseConnection(
        settings.DB_SERVER,
        settings.DB_DATABASE,
        settings.DB_USERNAME,
        settings.DB_PASSWORD,
    ) as db:
        response = db.execute_query(f'SELECT * FROM {settings.DB_SCHEMA}.ZLOGFAT')

        if response['status'] == 'success':
            for row in response['data']:
                print({row['NUMHAV_0']})
                print({row['STATUT_0']})
                print({row['INVDAT_0']})
                print(int(next(iter({row['ROWID']}))))
        else:
            print(response['message'])

    return

    # Check if exists files to be processed
    fileHandler = HandleFiles(settings.FOLDER_XML_IN, settings.FOLDER_XML_OUT)

    xml_list = fileHandler.check_for_xml_files()

    if not xml_list:
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
