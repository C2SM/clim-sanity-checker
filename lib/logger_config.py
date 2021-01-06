# standard modules
import logging
import sys

# standalone imports
from lib.color import colors

'''
Module providing all classes and functions
related to logging. It contains:

    - log: logger instance used in all other modules

    - CustomFormatter: format log-messages for each log-level
    
    - ShutdownHandler: define additional action for level "error"

    - banner: additional log-level for important steps in scripts

    - init_logger: put all extras into logger, init logger


J.Jucker 12.2020 (C2SM)

'''

log = logging.getLogger()

class CustomFormatter(logging.Formatter):

    format_debug = "     %(levelname)s: %(message)s (%(filename)s)"
    format_info = "%(message)s"
    format_banner = "=========  %(message)s"
    format_warning = "%(levelname)s: %(message)s (%(filename)s)"
    format_error = "%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: colors['black'] + format_debug + colors['reset'],
        logging.INFO: colors['black'] + format_info + colors['reset'],
        25: colors['green'] + format_banner + colors['reset'],
        logging.WARNING: colors['orange'] + format_warning + colors['reset'],
        logging.ERROR: colors['bold_red'] + format_error + colors['reset'],
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class ShutdownHandler(logging.Handler):

    def emit(self, record):
        logging.shutdown()
        sys.exit(1)

def banner(self, message, *args, **kws):
           self._log(25, message, args, **kws) 

def init_logger(lverbose):

    if lverbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log.setLevel(level)

    logging.addLevelName(25,"BANNER")
    logging.Logger.banner = banner

    ch = logging.StreamHandler()
    ch.setLevel(level)

    ch.setFormatter(CustomFormatter())

    log.addHandler(ch)

    # shutdown in case of logging.ERROR
    log.addHandler(ShutdownHandler(level=logging.ERROR)) 
