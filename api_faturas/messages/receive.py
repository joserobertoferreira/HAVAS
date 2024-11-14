import json

import requests


class ListQueuedMessages:
    def get_messages(base_url, receiver, headers):
        # Implementa a lógica para recuperar as mensagens
        service_url = f'https://{base_url}/ListQueuedMessageIds?Receiver={receiver}'

        response = requests.get(service_url, headers=headers)

        json_response = json.loads(response.text)

        return_message = {
            'CorrelationId': json_response['CorrelationId'],
            'Errors': json_response['Errors'],
            'headers': headers,
            'Messages': [],
        }

        if json_response['IsValid']:
            # Reduz o número de IDs de mensagens
            json_response['ResultData']['MessageIds'] = json_response['ResultData'][
                'MessageIds'
            ][:1]

            return_message['Messages'] = json_response['ResultData']['MessageIds']

        return return_message
