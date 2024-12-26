from config import settings
from messages.download import DownloadMessages
from services.authentication import AuthenticationService
from services.file_handler import FileHandlerService
from services.message_processor import MessageProcessorService
from utils.handle_files import HandleFiles


def api_messages():
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

            # Marking the message as processed
            # for message in messages:
            # MessageProcessorService(token).mark_as_processed(message['ResultData'])

            # Logout from API
            auth_service.logout(token['Token'])

            # Process the downloaded messages
            if len(messages) != 0:
                file_handler = FileHandlerService(
                    settings.BASE_DIR, settings.FOLDER_XML_IN, settings.FOLDER_XML_OUT
                )

                # Create the xml message files
                file_handler.create_message_files(messages)

                # Read the xml message files and process them
                message = MessageProcessorService()

                lists = message.process_messages(file_handler, settings.FOLDER_XML_OUT)

                for key, value in lists.items():
                    if key == 'status':
                        status_list = value
                    elif key == 'errors':
                        errors_list = value
                    elif key == 'sent':
                        sent_list = value
                    elif key == 'put_away':
                        put_away_files = value

                # Log the status and errors
                message.handle_xml.folder_input = settings.FOLDER_XML_OUT

                message.log_status_and_errors(
                    message.handle_xml, status_list, errors_list, sent_list
                )

                # Move to archive folder
                for xml_file in status_list + errors_list + sent_list + put_away_files:
                    HandleFiles.move_file(
                        xml_file,
                        settings.FOLDER_XML_OUT,
                        settings.FOLDER_XML_OUT / 'archive',
                    )


if __name__ == '__main__':
    api_messages()
