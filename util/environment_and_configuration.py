import os

from service.exceptions.EnvironmentalVariableNotFoundError import (
    EnvironmentalVariableNotFoundError,
)


def get_environment_variable(
    key: str, optional: bool = False, default=None
) -> str | None:
    """Loads an environment variable

    Args:
        key (str): key of the variable
        optional (bool, optional): whether an exception shall be raised if not availlable. Defaults to False.
        default (_type_, optional): Defaul value if optional is True. Defaults to None.

    Returns:
        str | None: the value or None

    Raises:
        EnvironmentalVariableNotFoundError: if not optional but key not found
    """
    value: str | None = os.getenv(key, default=None)

    if value is None:
        if optional:
            value = default
        else:
            raise EnvironmentalVariableNotFoundError(key=key)

    return value


def get_environment_variable_int(
    key: str, optional: bool = False, default=None
) -> int | None:
    """Loads an environment variable

    Args:
        key (str): key of the variable
        optional (bool, optional): whether an exception shall be raised if not availlable. Defaults to False.
        default (_type_, optional): Defaul value if optional is True. Defaults to None.

    Returns:
        int | None: the value or None

    Raises:
        EnvironmentalVariableNotFoundError: if not optional but key not found
    """
    return int(get_environment_variable(key, optional, default))
