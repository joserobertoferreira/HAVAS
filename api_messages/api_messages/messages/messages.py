import json
import uuid
from typing import Any, Dict

import requests
from config import settings
from database.database import Condition, DatabaseConnection
from utils.handle_files import HandleFiles


class Messages:
    def __init__(self, base_url: str = '', authentication: Dict[str, Any] = {}) -> None:
        if len(base_url) != 0:
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
    def update_invoice(document_number: str) -> bool:
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            # Update table ZSINVOICEV
            table_name = f'{settings.DB_SCHEMA}.ZSINVOICEV'
            set_columns = {'ZSTATUS_0': 8}
            where_clause = {'NUMX3_0': Condition('=', document_number)}

            response = db.execute_update(
                table_name,
                set_columns,
                where_clause,
            )

            if response['status'] == 'success':
                # Update table ZLOGFAT
                table_name = f'{settings.DB_SCHEMA}.ZLOGFAT'
                set_columns = {'STATUT_0': 7}
                where_clause = {'SIHNUM_0': Condition('=', document_number)}

                response = db.execute_update(
                    table_name,
                    set_columns,
                    where_clause,
                )

            return response['status'] == 'success'

    @staticmethod
    def update_log(data_log: Dict[str, Any]) -> None:
        try:
            with DatabaseConnection(
                settings.DB_SERVER,
                settings.DB_DATABASE,
                settings.DB_USERNAME,
                settings.DB_PASSWORD,
            ) as db:
                table_name = f'{settings.DB_SCHEMA}.ZSAPHLOG'

                current_date = HandleFiles.get_current_date_time()

                payload = {
                    'NUM_0': data_log['document_number'],
                    'NUMLIG_0': data_log['info_index'],
                    'STATUT_0': data_log['status'],
                    'ERRORCODE_0': data_log['info_code'],
                    'NOTE_0': data_log['info_note'],
                    'CREDATTIM_0': data_log['document_date'],
                    'UPDDATTIM_0': current_date,
                    'AUUID_0': uuid.uuid4(),
                    'CREUSR_0': 'INTER',
                    'UPDUSR_0': 'INTER',
                }

                response = db.execute_insert(table_name, payload)

                if response['status'] == 'success':
                    if data_log['status'] == 'ACCEPTED':
                        Messages.update_invoice(data_log['document_number'])

                    print(f'Log inserted for file {payload["NUM_0"]}.')
                else:
                    print(f'Failed to insert log for file {payload["NUM_0"]}.')
        except Exception as e:
            print(f'Error inserting log: {e}')
            raise e
