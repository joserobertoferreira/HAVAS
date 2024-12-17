import json
from typing import Any, Dict

import requests
from messages.messages import Messages


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

    def process_messages(file_services: object, work_path: str) -> Dict[str, list[Any]]:
        """Process the downloaded messages"""

        status_files = []
        errors_files = []
        sent_files = []
        put_away_files = []

        # Check if exists files to be processed
        xml_list = file_services.check_for_xml_files(work_path)

        for xml_file in xml_list:
            if 'DOCUMENT_STATUS' in xml_file:
                status_files.append(xml_file)
            elif 'DOCSTS_ERROR' in xml_file:
                errors_files.append(xml_file)
            elif 'DOCSTS_SENT' in xml_file:
                sent_files.append(xml_file)
            else:
                put_away_files.append(xml_file)

        return {
            'status': status_files,
            'errors': errors_files,
            'sent': sent_files,
            'put_away': put_away_files,
        }

    @staticmethod
    def log_document(
        xml_handler: object, document_list: list[str], document_type: str
    ) -> None:
        # Process the errors files
        for document in document_list:
            documents = xml_handler.convert_xml_to_dict(document)
            if not documents:
                continue

            message = documents.get('msg:message', {})
            if not message:
                continue

            document_date = message.get('@creationDateTime', '')

            document_status = message.get('doc:documentStatus', {})
            if not document_status:
                continue

            document_number = document_status.get('@documentNumber', '')
            status_information = document_status.get('statusInformation', {})

            status = status_information.get('status', '')

            if document_type == 'documentSent':
                document_info = {'code': status, 'note': 'Document sent successfully'}
            else:
                document_info = status_information.get(document_type, {})

            if isinstance(document_info, dict):
                document_info = [document_info]

            for index, info in enumerate(document_info):
                info_code = info.get('code', '')
                info_note = info.get('note', '')

                # If the document is a status file and an error code is not
                # ERROR then log the information
                if status == 'information' and info_code != 'ERROR':
                    # Log each information separately
                    Messages.update_log({
                        'document_number': document_number,
                        'document_date': document_date,
                        'status': status,
                        'info_code': info_code,
                        'info_note': info_note,
                        'info_index': index,
                    })
