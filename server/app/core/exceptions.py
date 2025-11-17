class ErrorParsingMMIO(Exception):
    ...


class ErrorSavingData(Exception):
    ...


class NodeDoesNotExist(Exception):
    ...


class MultipleNodesFound(Exception):
    ...


class ErrorConstructingQuery(Exception):
    ...


class QueryIsRequired(Exception):
    ...


class ConnectorError(Exception):
    ...


class DistributionNotFound(Exception):
    ...


class InvalidDatasetError(Exception):
    ...


class GraphValidationError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details: list[dict[str, str]] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
