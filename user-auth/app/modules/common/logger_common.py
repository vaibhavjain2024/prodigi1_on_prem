import logging
import sys
import json
from datetime import datetime

def get_logger():
    #region log setup
    logger = logging.getLogger()
    log_stream_handler = logging.StreamHandler(stream=sys.stdout)
    log_stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_stream_handler.setFormatter(formatter)
    logger.addHandler(log_stream_handler)
    #endregion
    return logger

# def prepare_lambda_response(message, status_code):
#     if (
#         isinstance(message, dict)
#         or isinstance(message, list)
#         or isinstance(message, str)
#     ):
#         message = json.dumps(message)
#     return {"statusCode": status_code, "body": message}

# def get_logger(logFile, name):
    
#     logger = logging.getLogger(name)
    
#     if logger.hasHandlers():
#         return logger
    
#     logger.setLevel(logging.INFO)

#     log_file_handler = logging.FileHandler(logFile)
#     log_file_handler.setLevel(logging.INFO)
    
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     log_file_handler.setFormatter(formatter)

#     logger.addHandler(log_file_handler)

#     return logger

# logFile = f'../../logs/{datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}.log'
# logger = get_logger(logFile)



