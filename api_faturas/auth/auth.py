import json

import requests


class Auth:
    def login(base_url, username, password):
        service_url = f'https://{base_url}/GetTokenFromLogin'

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
