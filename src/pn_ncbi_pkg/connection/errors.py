class NCBIConnectionError(ConnectionError):
    """Base class for NCBI connection failures."""


class ConnectionConfigError(ValueError):
    """The submission YAML or protocol configuration is invalid."""


class MissingConnectionSettingError(ConnectionConfigError):
    """A required connection setting is missing from submission YAML."""


class UnsupportedProtocolError(ConnectionConfigError):
    """The requested protocol is not supported."""

