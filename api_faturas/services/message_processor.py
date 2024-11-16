from config import settings
from messages.messages import Messages
from messages.processed import ProcessedMessage
from messages.receive import ListQueuedMessages


class MessageProcessorService:
    def __init__(self, token: dict):
        self.base_url = settings.SERVER_BASE_ADDRESS
        self.handle_messages = Messages(self.base_url, token)
        self.message_headers = token['headers']

    def send_message(self, sender: str, file: str, file_base64: str) -> bool:
        sent_message = self.handle_messages.send_message(sender, file, file_base64)

        if sent_message:
            print(f'Message sent successfully for file {file}.')

        return sent_message

    def update_database(self, file: str) -> bool:
        update_ok = self.handle_messages.update_database(file)

        if update_ok:
            print(f'Database updated for file {file}.')
        else:
            print(f'Failed to update database for file {file}.')

        return update_ok

    def get_messages(self) -> dict:
        message_list = ListQueuedMessages.get_messages(
            self.base_url, settings.SENDER, self.message_headers
        )

        return message_list

    def mark_as_processed(self, message: dict) -> bool:
        processed = ProcessedMessage.mark_as_processed(
            self.base_url, self.message_headers, message
        )

        if processed:
            print('Message marked as processed.')
        else:
            print('Failed to mark message as processed.')

        return processed
