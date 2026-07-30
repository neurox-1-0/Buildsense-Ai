class BuildSenseError(Exception):
    """Base application exception."""


class ExternalToolError(BuildSenseError):
    """Raised when an external source cannot be queried."""


class ValidationError(BuildSenseError):
    """Raised when evidence or model output is invalid."""
