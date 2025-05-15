import logging
from os import makedirs
from logging.handlers import TimedRotatingFileHandler

def get_logger(name, logFileName):

    LOGDIR = "./logs"
    ROTATELOG = "midnight"
    INTERVAL = 1
    BACKUPCOUNT = 3

    logFilePath = f'{LOGDIR}/{logFileName}.log'

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False # Set this to false to avoid conflict with uvicorn logger 

    if not logger.handlers:

        makedirs(LOGDIR, exist_ok=True)

        handler = TimedRotatingFileHandler(
            filename = logFilePath,
            when = ROTATELOG,
            interval = INTERVAL,
            backupCount = BACKUPCOUNT,
            encoding = 'utf-8',
            utc = True
        )

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger