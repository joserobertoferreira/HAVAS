import json


class ProcessedMessages:
    def __init__(self, base_url, authentication) -> None:
        self.service_url = f'https://{base_url}/ReceiveMessage'
        self.headers = {
            'Authorization': 'Bearer ' + authentication['Token'],
            'Content-type': 'application/json',
        }
        self.receiver = 'urn:netdoc:qa'
        self.message_id = authentication['CorrelationId']

    def send_message(self, sender, file, fileBase64) -> None:
        payload = {
            'Sender': sender,
            'Receiver': self.receiver,
            'ContentType': 'application/xml',
            'Base64Data': fileBase64,
            'MessageId': self.message_id,
            'Filename': file,
        }

        request_data = json.dumps(payload)

        # response = requests.post(self.service_url, headers=self.headers, json=payload)
        # print(response.json())
