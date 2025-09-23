import logging
import traceback
from datetime import datetime

def setup_file_logger(name: str, log_file: str, level=logging.ERROR):
    """
    Sets up a logger to write to a specific file.

    To prevent duplicate handlers if called multiple times, it first checks
    if the logger already has handlers.

    Args:
        name (str): The name of the logger.
        log_file (str): The path to the log file.
        level: The logging level. Defaults to logging.ERROR.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.FileHandler(log_file)
        # A more detailed format similar to the MATLAB script's intention
        formatter = logging.Formatter(
            'Code ran on %(asctime)s\n%(message)s',
            datefmt='%d-%b-%Y %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def log_error_to_file(logger: logging.Logger, subject_name: str, exception: Exception):
    """
    Formats an error message and writes it to the log file.
    Replicates the behavior of `write_error` in the MATLAB script.

    Args:
        logger (logging.Logger): The logger instance to use.
        subject_name (str): The name of the subject being processed.
        exception (Exception): The exception object that was caught.
    """
    tb_str = traceback.format_exc()

    message = (
        f"\n#################################################################\n"
        f"Subject Name: {subject_name}\n\n"
        f"Error Type: {type(exception).__name__}\n"
        f"Error Message: {str(exception)}\n\n"
        f"Traceback:\n{tb_str}"
        f"#################################################################\n"
    )

    logger.error(message)
