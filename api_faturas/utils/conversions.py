import base64
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Optional

from dateutil import parser


class Conversions:
    @staticmethod
    def convert_value(value: Any, precision: int = 0) -> Any:
        if isinstance(value, str):
            return_value = Conversions._convert_str(value)
        elif isinstance(value, int):
            return_value = value
        elif isinstance(value, float):
            return_value = Conversions._convert_float(value, precision)
        elif isinstance(value, bool):
            return_value = value
        elif value is None:
            return_value = value
        elif isinstance(value, datetime):
            return_value = value
        elif isinstance(value, date):
            return_value = value
        elif isinstance(value, Decimal):
            return_value = Conversions._convert_decimal(value, precision)
        elif isinstance(value, list):
            return_value = Conversions._convert_list(value)
        else:
            return_value = value

        return return_value

    @staticmethod
    def _convert_str(value: str) -> str:
        return value.strip()

    @staticmethod
    def _convert_float(value: float, precision: Optional[int]) -> float:
        if precision != 0:
            return round(value, precision)
        return value

    @staticmethod
    def _convert_decimal(value: Decimal, precision: Optional[int]) -> Decimal:
        if value.is_normal():
            if precision != 0:
                return round(value, precision)
            return value
        else:
            return Decimal(0)

    @staticmethod
    def convert_to_datetime(value: str, default: bool = False) -> datetime:
        """
        Convert a string to a datetime object in ISO UTC format.

        Parameters:
            value (str): String to be converted.
            default (bool): Defines whether to return datetime(1900, 1, 1) in ISO UTC
              format in case of error.

        Returns:
            str: The converted date in ISO UTC format, or datetime(1900, 1, 1) in case of
              error (if default=True).
        """
        try:
            # First, try to convert directly to ISO format.
            return parser.isoparse(value)
        except (ValueError, TypeError):
            pass

        try:
            # Try a generic conversion using dateutil.parser.parse.
            return parser.parse(value)
        except (ValueError, TypeError):
            pass

        # If the string is empty or no conversion was possible.
        if not value or default:
            return datetime(1900, 1, 1)

        # If no conversion is possible and default=False, return None.
        return None

    @staticmethod
    def convert_to_date(value: str, default: bool = False) -> date:
        """
        Convert a string to a date object.

        Parameters:
            value (str): String to be converted.
            default (bool): Defines whether to return date(1900, 1, 1) in case of error.

        Returns:
            date: The converted date object or date(1900, 1, 1) in case of error
              (if default=True).
        """
        try:
            # First, try to convert directly to ISO format and extract the date.
            return parser.isoparse(value).date()
        except (ValueError, TypeError):
            pass

        try:
            # Try a generic conversion using dateutil.parser.parse and extract the date.
            return parser.parse(value).date()
        except (ValueError, TypeError):
            pass

        # If the string is empty or no conversion was possible.
        if not value or default:
            return date(1900, 1, 1)

        # If no conversion is possible and default=False, return None.
        return None

    @staticmethod
    def _convert_list(value: list) -> list:
        return [Conversions.convert_value(item) for item in value]

    @staticmethod
    def convert_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converte os valores de um dicionário para uma forma mais legível.

        Args:
            data (dict): Dicionário com chave e valor a ser convertido.

        Returns:
            dict: Novo dicionário com os valores convertidos.
        """

        return {key: Conversions.convert_value(value) for key, value in data.items()}

    @staticmethod
    def generate_sql_with_values(query, values):
        """
        Gera a query SQL com valores reais substituindo os placeholders.

        :param query: A consulta SQL com placeholders (?)
        :param values: A lista de valores que substituirão os placeholders
        :return: A query com valores reais
        """
        # Substituir os placeholders (?) pelos valores reais
        # Primeiro, formatar os valores para evitar erro com tipos
        formatted_values = [repr(v) for v in values]

        # Substituir os placeholders (?):
        for value in formatted_values:
            query = query.replace('?', value, 1)  # Substituir um placeholder por vez

        return query

    @staticmethod
    def convert_file_to_base64(file_path: str, file_name: str) -> str:
        file_attributes = Path(file_path) / file_name

        base_string = ''

        # Open the file in binary mode and read its content
        if file_attributes.is_file():
            with file_attributes.open('rb') as file:
                content = file.read()
                base_string = base64.b64encode(content).decode('utf-8')

        return base_string

    @staticmethod
    def is_number(value):
        try:
            # Try to convert the value to a number (int or float)
            float_value = float(value)

            # Check if the converted number is an integer or decimal
            if float_value.is_integer():
                return 'integer'
            else:
                return 'decimal'
        except ValueError:
            # Return None if it's not possible to convert
            return None
