class EnvironmentalVariableNotFoundError(Exception):
    def __init__(self, key: str) -> None:
        super().__init__(
            f"The environmental variable {key} is not available but set to required!"
        )
