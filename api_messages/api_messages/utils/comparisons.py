import operator
import re
from typing import Any


def compare(operator_str: str, first_value: Any, second_value: Any, extra=None) -> bool:
    """
    Function that receives an operator as a string, two or three arguments, and
    returns the result of the comparison between the values.

    Parameters:
    - operator_str: the operator to be used (>, <, =, IN, LIKE, etc.).
    - first_value: first value (left side of the comparison).
    - second_value: second value (right side of the comparison or list of values
    for operators like IN).
    - extra (optional): a third value needed for the BETWEEN operator.

    Returns:
    - bool: True if the condition is met, otherwise False.
    """
    # Check if the type of the values to be compared is the same
    if not isinstance(first_value, type(second_value)):
        return False

    # Dictionary of supported operators
    operators = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq,
        '!=': operator.ne,
        '<>': operator.ne,  # SQL compatibility
        'isEmpty': lambda first_value, _: not bool(first_value),
        'isNotEmpty': lambda first_value, _: bool(first_value),
        'LIKE': lambda first_value, second_value: re.search(
            second_value.replace('%', '.*'), first_value
        )
        is not None
        if isinstance(first_value, str) and isinstance(second_value, str)
        else False,
        'IN': lambda first_value, second_value: first_value in second_value
        if isinstance(second_value, (list, tuple, set))
        else False,
        'NOT IN': lambda first_value, second_value: first_value not in second_value
        if isinstance(second_value, (list, tuple, set))
        else False,
        'BETWEEN': lambda first_value, second_value, extra: second_value
        <= first_value
        <= extra
        if second_value is not None and extra is not None
        else False,
        'NOT BETWEEN': lambda first_value, second_value, extra: not (
            second_value <= first_value <= extra
        )
        if second_value is not None and extra is not None
        else False,
        'IS NULL': lambda first_value, _: first_value is None,
        'IS NOT NULL': lambda first_value, _: first_value is not None,
        'EXISTS': lambda first_value, _: bool(first_value),
        # Supposes 'first_value' is a list or subquery that returns results
    }

    # Checks if the operator is supported
    if operator_str not in operators:
        return False
    #        raise ValueError(f"Operator '{operator}' is not supported.")

    # Check the number of required arguments
    if operator_str in {'BETWEEN', 'NOT BETWEEN'}:
        if extra is None:
            raise ValueError(
                f"The operator '{operator_str}' requires a third argument (upper bound)."
            )
        return operators[operator_str](first_value, second_value, extra)
    else:
        return operators[operator_str](first_value, second_value)
