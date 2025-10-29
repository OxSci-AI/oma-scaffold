from oxsci_shared_core.config import BaseConfig


class Config(BaseConfig):
    """
    Service configuration class extending BaseConfig from oxsci-shared-core.

    Add your custom configuration variables here as needed.
    """

    SERVICE_PORT: int = 8080


config = Config()
