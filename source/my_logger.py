import logging
import logging.handlers
import os

LOG_D = 'logs'
DEBUG_D = 'debug'
DATE_FORMAT = "%d-%b-%Y_%H:%M:%S"

### Logging ###
class LevelFilter(logging.Filter):
	def __init__(self, level):
		self.level = level

	def filter(self, record):
		return record.levelno == self.level

def create_logger(name):
	logger = logging.getLogger(name)
	logger.setLevel(logging.INFO)

	debug = os.path.join(LOG_D, DEBUG_D)
	if not os.path.exists(debug):
		os.makedirs(debug)
		
	debug_handler = logging.FileHandler(os.path.join(debug, 'debug.log'))
	debug_handler.setLevel(logging.DEBUG)
	debug_formatter = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s %(message)s", DATE_FORMAT)
	debug_handler.setFormatter(debug_formatter)
	debug_handler.addFilter(LevelFilter(logging.DEBUG))

	info_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(LOG_D, 'tools.log'), when='W0', backupCount=52, delay=True)
	info_handler.setLevel(logging.INFO)
	info_formatter = logging.Formatter("%(message)s")
	info_handler.setFormatter(info_formatter)
	info_handler.addFilter(LevelFilter(logging.INFO))

	other_handler = logging.StreamHandler()
	other_handler.setLevel(logging.WARNING)
	other_formatter = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s %(message)s", DATE_FORMAT)
	other_handler.setFormatter(other_formatter)

	logger.addHandler(debug_handler)
	logger.addHandler(info_handler)
	logger.addHandler(other_handler)
	
	return logger