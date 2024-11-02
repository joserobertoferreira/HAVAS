from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict


class Conversions:
    @staticmethod
    def convert_value(value: Any) -> Any:  # noqa: PLR0911
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, int):
            return value
        elif isinstance(value, float):
            return value
        elif isinstance(value, bool):
            return value
        elif value is None:
            return value
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            return value
        elif isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, list):
            # Aplica a formatação em cada item da lista mantendo o tipo
            return [Conversions.convert_value(item) for item in value]
        else:
            return value  # Retorna outros tipos diretamente

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
