import json
import sys
import os
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create loggers
time_logger = logging.getLogger('time_logger')
error_logger = logging.getLogger('error_logger')
gemini_logger = logging.getLogger('gemini_logger')
process_logger = logging.getLogger('process_logger')

# Set log levels
time_logger.setLevel(logging.INFO)
error_logger.setLevel(logging.ERROR)
gemini_logger.setLevel(logging.INFO)
process_logger.setLevel(logging.INFO)

# Create file handlers
time_handler = logging.FileHandler('logs/time.log')
error_handler = logging.FileHandler('logs/errors.log')
gemini_handler = logging.FileHandler('logs/gemini.log')
process_handler = logging.FileHandler('logs/process.log')

# Create formatters and add them to the handlers
formatter = logging.Formatter('%(asctime)s - %(message)s')
time_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
gemini_handler.setFormatter(formatter)
process_handler.setFormatter(formatter)

# Add handlers to the loggers
time_logger.addHandler(time_handler)
error_logger.addHandler(error_handler)
gemini_logger.addHandler(gemini_handler)
process_logger.addHandler(process_handler)





