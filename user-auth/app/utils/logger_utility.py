import  logging

logging.basicConfig(
    level=logging.INFO,  # Set log level
    format="%(asctime)s - prodigi1 - %(levelname)s - %(message)s",  # Log message format
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("app.log"),  # Log to a file
    ]
)

logger = logging.getLogger(__name__)
