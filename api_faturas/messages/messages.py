import json
from typing import Any, Dict

import requests


class ProcessedMessages:
    def __init__(self, base_url: str, authentication: Dict[str, Any]) -> None:
        self.service_url = f'https://{base_url}/ReceiveMessage'
        self.headers = {
            'Authorization': 'Bearer ' + authentication['Token'],
            'Content-type': 'application/json',
        }
        self.receiver = 'urn:netdoc:qa'
        self.message_id = authentication['CorrelationId']

    def send_message(self, sender: str, file: str, fileBase64: Any) -> bool:
        payload = {
            'Sender': sender,
            'Receiver': self.receiver,
            'ContentType': 'application/xml',
            'Base64Data': fileBase64,
            'MessageId': self.message_id,
            'Filename': f'{file}.xml',
        }

        request_data = json.dumps(payload)

        response = requests.post(
            self.service_url, headers=self.headers, data=request_data
        )

        json_response = json.loads(response.text)

        return json_response['IsValid']
