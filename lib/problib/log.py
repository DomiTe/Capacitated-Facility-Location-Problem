import structlog
from rich_structlog import setup_logging

setup_logging(
    pkg2loglevel={
        "tornado": "WARNING",
    }
)


log: structlog.stdlib.BoundLogger = structlog.get_logger()
