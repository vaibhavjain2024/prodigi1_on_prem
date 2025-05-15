import logging
from datetime import datetime
import pytz

class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Convert to IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        dt = datetime.fromtimestamp(record.created).astimezone(ist)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

# Create a custom formatter with colors and better formatting
class ColoredFormatter(ISTFormatter):
    """Custom formatter with colors and better formatting"""
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        # Use ISTFormatter instead of logging.Formatter to ensure IST timezone is used
        formatter = ISTFormatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S IST')
        return formatter.format(record)

# Create logger
logger = logging.getLogger("PRODIGI-I - BATCH SERVICE")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()

# Create formatter and add it to handler
console_formatter = ColoredFormatter()
console_handler.setFormatter(console_formatter)

# Add handler to the logger
logger.addHandler(console_handler)
