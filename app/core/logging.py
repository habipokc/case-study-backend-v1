import logging
import sys
from typing import Any

from app.core.config import settings

class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages to Loguru or just standard logging configuration
    """
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    """
    Configure logging with JSON formatting
    """
    # Simply using standard logging with basic config for this implementation
    # In a real production apps, could use 'loguru' or 'structlog' 
    # But to keep dependencies minimal as per requirements.txt, we use standard logging with a nice format.
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if settings.PROJECT_NAME == "Case Study": # We can check environment here
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    # Set log level for some noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

logger = logging.getLogger("app")
