import json
from typing import Any, Dict

import requests

SERVER_ERROR_CODE = 500


class Auth:
    def __init__(self, base_url: str) -> None:
        self.base_url = f'https://{base_url}'

    def login(self, username: str, password: str) -> Dict[str, Any]:
        service_url = f'{self.base_url}/GetTokenFromLogin'

        query_params = {'userId': username, 'password': password}

        response = requests.get(service_url, params=query_params)

        json_response = json.loads(response.text)

        correlationId = json_response['CorrelationId']
        resultData = json_response['ResultData']
        resultCode = json_response['ResultCode']
        errors = json_response['Errors']

        return {
            'HttpStatus': resultCode,
            'CorrelationId': correlationId,
            'Token': resultData,
            'Errors': errors,
        }

    def logout(self, token: str) -> int:
        service_url = f'{self.base_url}/Logout'

        headers = {'Authorization': 'Bearer ' + token}

        response = requests.get(service_url, headers=headers)

        if response.status_code < SERVER_ERROR_CODE:
            json_response = json.loads(response.text)

            return json_response['ResultCode']

        return 0
