import json

import requests


class ProcessedMessage:
    def mark_as_processed(base_url: str, headers: dict, message: dict) -> dict:
        """After retrieving the documents from your queue, it is required to mark then as
        processed. This operation removes the document from the queue.
        """
        service_url = f'https://{base_url}/ChangeQueuedToProcessed'

        # Get the message from the list
        sender = message['Sender']
        receiver = message['Receiver']
        messageId = message['MessageId']

        payload = {'Sender': sender, 'Receiver': receiver, 'MessageId': messageId}

        # Payload goes in json, serialize the payload object to json
        request_data = json.dumps(payload)

        # POST request to get a token
        response = requests.request(
            'POST', service_url, data=request_data, headers=headers
        )

        # Serialize the response
        json_response = json.loads(response.text)

        # return_message = {
        #     'CorrelationId': json_response['CorrelationId'],
        #     'Errors': json_response['Errors'],
        #     'headers': headers,
        #     'Messages': [],
        #     'IsValid': json_response['IsValid'],
        # }

        return json_response['IsValid']

    def process_messages(file_services: object, work_path: str) -> None:
        """Process the downloaded messages"""

        # Check if exists files to be processed
        xml_list = file_services.check_for_xml_files(work_path)

        for xml_file in xml_list:
            print(f'Processing file: {xml_file}')
