class ProcureBrainError(Exception):
    """Base application exception."""


class ExternalServiceError(ProcureBrainError):
    """Raised when an external dependency fails."""


class SearchError(ExternalServiceError):
    """Raised when web search fails."""


class FetchError(ExternalServiceError):
    """Raised when web fetching fails."""


class VectorStoreError(ExternalServiceError):
    """Raised when vector store operations fail."""


class ModelProviderError(ExternalServiceError):
    """Raised when a model provider call fails."""
