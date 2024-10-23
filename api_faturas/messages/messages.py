class ProcessedMessages:
    def __init__(self, base_url, authentication) -> None:
        self.service_url = f'https://{base_url}/ReceiveMessage'
        self.headers = {
            'Authorization': 'Bearer ' + authentication['Token'],
            'Content-type': 'application/json',
        }
        self.receiver = 'urn:netdoc:qa'
        self.message_id = authentication['CorrelationId']

    @staticmethod
    def send_message(sender, messages: dict) -> None:
        print(messages)

        for message in messages:
            print(message)

            # payload = {
            #     'sender': sender,
            #     'receiver': self.receiver,
            #     'content_type': 'application/xml',
            #     'base64_string': message['base64_string'],
            #     'message_id': self.message_id,
            #     'filename': message['filename'],
            # }

            # response = requests.post(self.service_url, headers=self.headers, json=payload)
            # print(response.json())
