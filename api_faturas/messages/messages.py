import json
from typing import Any, Dict

import requests

from config import settings
from database.database import Condition, DatabaseConnection


class Messages:
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

    @staticmethod
    def update_database(file: str) -> bool:
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            document_number = f'{file[:8]}/{file[8:]}'

            # Update table ZSINVOICEV
            table_name = f'{settings.DB_SCHEMA}.ZSINVOICEV'
            set_columns = {'ZSTATUS_0': 7}
            where_clause = {'NUMX3_0': Condition('=', document_number)}

            response = db.execute_update(
                table_name,
                set_columns,
                where_clause,
            )

            if response['status'] == 'success':
                # Update record table ZLOGFAT
                table_name = f'{settings.DB_SCHEMA}.ZLOGFAT'
                set_columns = {'STATUT_0': 7}
                where_clause = (
                    {
                        'NUM_0': Condition('=', document_number),
                        'NUMLIG_0': Condition('=', 0),
                    },
                )

                response = db.execute_update(
                    table_name,
                    set_columns,
                    where_clause,
                )

            return response['status'] == 'success'
