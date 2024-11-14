from config import settings
from messages.download import DownloadMessages
from messages.invoices import HandleInvoices
from services.authentication import AuthenticationService
from services.file_handler import FileHandlerService
from services.message_processor import MessageProcessorService


def api_faturas() -> None:
    # Get the invoices to be processed and parse them to XML
    HandleInvoices.get_invoices()

    # # Check if exists files to be processed
    file_handler = FileHandlerService(
        settings.BASE_DIR, settings.FOLDER_XML_IN, settings.FOLDER_XML_OUT
    )

    xml_list = file_handler.check_for_xml_files()

    if not xml_list:
        print('No files to be processed.')

        # return

    # Generate the base64 strings
    for file, file_base64 in file_handler.generate_base64_strings(xml_list).items():
        # Get the authentication token
        auth_service = AuthenticationService()
        token = auth_service.login(settings.API_USER, settings.API_PASSWORD)

        if token:
            message_service = MessageProcessorService(token)

            sent_message = message_service.send_message(
                settings.SENDER, file, file_base64
            )

            # Logout from API
            auth_service.logout(token['Token'])

            # If the message was sent, update database and move the file to the output folder  # noqa: E501
            if sent_message:
                message_service.update_database(file)
                file_handler.move_file(f'{file}.xml')

    # Check if exists messages to be retrieved

    # Get the authentication token
    auth_service = AuthenticationService()
    token = auth_service.login(settings.API_USER, settings.API_PASSWORD)

    if token:
        # Get the message list
        message_list = MessageProcessorService(token).get_messages()

        if len(message_list['Errors']) == 0:
            # Download the messages
            download = DownloadMessages(
                settings.SERVER_BASE_ADDRESS, token['headers'], message_list['Messages']
            )
            messages = download.download_messages()

            # Logout from API
            auth_service.logout(token['Token'])

            # Process the downloaded messages
            if len(messages) != 0:
                file_handler.create_message_files(messages)


if __name__ == '__main__':
    api_faturas()
