import json
from typing import Any

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

    def process_messages(file_services: object, work_path: str) -> Any:
        """Process the downloaded messages"""

        status_files = []
        errors_files = []

        # Check if exists files to be processed
        xml_list = file_services.check_for_xml_files(work_path)

        for xml_file in xml_list:
            if 'DOCUMENT_STATUS' in xml_file:
                status_files.append(xml_file)
            elif 'DOCSTS_ERROR' in xml_file:
                errors_files.append(xml_file)

        return status_files, errors_files

    @staticmethod
    def log_errors(xml_handler: object, errors_list: list[str]) -> None:
        # Process the errors files
        for error in errors_list:
            errors = xml_handler.convert_xml_to_dict(error)

            if errors:
                message = errors.get('msg:message', {})

                if message:
                    document_status = message.get('doc:documentStatus', {})

                    if document_status:
                        document_number = document_status.get('@documentNumber', '')
                        status = document_status.get('statusInformation', {}).get(
                            'status', ''
                        )
                        error_code = status.get('documentError', {}).get('code', '')
                        note = status.get('documentError', {}).get('note', '')

                        # Log the error
                        Messages.update_log({
                            'document_number': document_number,
                            'status': status,
                            'error_code': error_code,
                            'note': note,
                        })

    @staticmethod
    def log_status(xml_handler: object, status_list: list[str]) -> None:
        # Process the status files
        for statut in status_list:
            statuts = xml_handler.convert_xml_to_dict(statut)

            if statuts:
                message = statuts.get('msg:message', {})

                if message:
                    document_status = message.get('doc:documentStatus', {})

                    if document_status:
                        document_number = document_status.get('@documentNumber', '')
                        status = document_status.get('statusInformation', {}).get(
                            'status', ''
                        )
                        statut_code = status.get('documentError', {}).get('code', '')
                        note = status.get('documentError', {}).get('note', '')

                        # Log the status
                        Messages.update_log({
                            'document_number': document_number,
                            'status': status,
                            'error_code': statut_code,
                            'note': note,
                        })
