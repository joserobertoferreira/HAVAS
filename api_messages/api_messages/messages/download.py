import json

import requests


class DownloadMessages:
    def __init__(self, base_url, headers, messages) -> None:
        self.base_url = f'https://{base_url}/GetMessageData'
        self.headers = headers
        self.messages = messages

    def download_messages(self) -> list[str]:
        # Implementa a lógica para baixar as mensagens
        messages_data = []

        for message in self.messages:
            service_url = f'{self.base_url}?Receiver={message['Receiver']}'
            service_url += f'&MessageId={message["MessageId"]}'
            service_url += f'&Sender={message['Sender']}'

            response = requests.get(service_url, headers=self.headers)

            json_response = json.loads(response.text)

            messages_data.append(json_response)

        return messages_data
