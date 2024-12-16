import re
import uuid
from datetime import date, datetime
from pathlib import Path

from config import settings
from database.database import Condition, DatabaseConnection
from utils.conversions import Conversions, HandleFiles


class ValidatorData:
    @staticmethod
    def execute_validation(value: str, data: dict, enum: dict) -> dict:
        """
        Execute the validation logic for a single attribute.
        """
        data_type = data.get('data_type', '')
        pattern = data.get('pattern', '')

        if data_type:
            if 'Enum' in data_type:
                data['enum'] = enum.get(data_type, [])
                data['data_type'] = 'enum'
            elif pattern:
                data['data_type'] = 'pattern'

            validator = Validator(data)
            result = validator.validate(value)

            return result

        return None

    @staticmethod
    def delete_previous_errors(file: Path) -> None:
        """
        Delete previous errors from the database.
        """
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            file_name = file.stem

            # Delete previous errors if exists
            table_name = f'{settings.DB_SCHEMA}.ZLOGFAT'
            where_clause = {
                'SIHNUM_0': Condition('=', f'{file_name[:8]}/{file_name[8:]}').as_tuple(),
                'STATUT_0': Condition('=', 'ERROR').as_tuple(),
            }

            db.execute_delete(table_name, where_clause)

    @staticmethod
    def update_database(
        file: Path, parent_process: str | None, process: str, message: str
    ) -> None:
        """
        Update the database with the validation error.
        """
        with DatabaseConnection(
            settings.DB_SERVER,
            settings.DB_DATABASE,
            settings.DB_USERNAME,
            settings.DB_PASSWORD,
        ) as db:
            document_number = f'{file.stem[:8]}/{file.stem[8:]}'
            next_number = 0

            # Read the last error number
            result_query = db.execute_query(
                table=f'{settings.DB_SCHEMA}.ZLOGFAT',
                columns=['NUMLIG_0'],
                where_clauses={
                    'SIHNUM_0': Condition('=', document_number).as_tuple(),
                },
                order_by=('NUMLIG_0 DESC', 1),
            )

            # Check if the query was successful
            if result_query['status'] == 'success':
                next_number = int(result_query['data'])

            next_number += 1

            # Update table ZLOGFAT
            table_name = f'{settings.DB_SCHEMA}.ZLOGFAT'

            if parent_process:
                update_string = f'{parent_process} -> {process}: {message}'
            else:
                update_string = f'{process}: {message}'

            current_date = HandleFiles.get_current_date_time()

            payload = {
                'NUM_0': document_number,
                'NUMLIG_0': str(next_number),
                'STATUT_0': 'ERROR',
                'ERRORCODE_0': 'VALIDATION',
                'NOTE_0': update_string,
                'CREDATTIM_0': current_date,
                'UPDDATTIM_0': current_date,
                'AUUID_0': uuid.uuid4(),
                'CREUSR_0': 'INTER',
                'UPDUSR_0': 'INTER',
            }

            db.execute_insert(table_name, payload)


class Validator:
    def __init__(self, config):
        """
        Initialize the validator with a configuration dictionary.

        Args:
            config (dict): The configuration containing validation rules.
        """
        self.config = config

    def validate(self, value):
        """
        Validate the provided value against the configuration rules.

        Args:
            value (str): The value to be validated.

        Returns:
            dict: A dictionary with the validation result.
        """

        def fail(message):
            return {'status': 'error', 'message': self.config.get('message', message)}

        # Validation rules
        validations = {
            'string': lambda v: isinstance(v, str),
            'nonEmptyString': lambda v: isinstance(v, str) and bool(v.strip()),
            'integer': lambda v: Validator._try_cast(v, int),
            'decimal': lambda v: Validator._try_cast(v, float),
            'boolean': lambda v: v in {'true', 'false', True, False},
            'date': lambda v: Validator._try_date(v, '%Y-%m-%d'),
            'datetime': lambda v: Validator._try_date(v, '%Y-%m-%dT%H:%M:%S.%f'),
            'enum': lambda v: v in self.config.get('enum', []),
            'pattern': lambda v: Validator._try_regex(v, self.config.get('pattern')),
        }

        # Required field validation
        if self.config.get('required', False) and not value:
            return fail('Missing required value.')

        # Data type validation
        expected_type = self.config.get('data_type')
        if expected_type in validations and not validations[expected_type](value):
            return fail(f'Invalid {expected_type} value.')

        # Length constraints
        min_length = self.config.get('minLength')
        max_length = self.config.get('maxLength')

        if min_length is not None and len(value) < min_length:
            return fail(f'Value is shorter than {min_length} characters.')

        if max_length is not None and len(value) > max_length:
            return fail(f'Value exceeds {max_length} characters.')

        # If all checks pass
        return {'status': 'success', 'message': 'Validation passed.'}

    @staticmethod
    def _try_cast(value, cast_type):
        try:
            cast_type(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _try_date(value, date_format):
        date_time = Conversions.convert_to_datetime(value, date_format, default=False)

        return isinstance(date_time, (date, datetime)) and bool(date_time)

    @staticmethod
    def _try_regex(value, pattern):
        return bool(pattern and re.fullmatch(pattern, value))
