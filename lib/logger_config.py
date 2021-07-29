# standard modules
import logging
import sys
import os

# standalone imports
from lib.color import colors

'''
Module providing all classes and functions
related to logging. It contains:

    - log: logger instance used in all other modules

    - FormatterColor: format log-messages for each log-level with color

    - FormatterNoColor: format log-messages for each log-level without color

    - ShutdownHandler: define additional action for level "error"

    - banner: additional log-level for important steps in scripts

    - init_logger: put all extras into logger, init logger


J.Jucker 12.2020 (C2SM)

'''

log = logging.getLogger()

class FormatterColor(logging.Formatter):

    format_debug = "     %(levelname)s: %(message)s (%(filename)s)"
    format_info = "%(message)s"
    format_banner = "=========  %(message)s"
    format_warning = "%(levelname)s: %(message)s (%(filename)s)"
    format_error = "%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: colors['reset'] + format_debug,
        logging.INFO: colors['reset'] + format_info,
        25: colors['green'] + format_banner + colors['reset'],
        logging.WARNING: colors['orange'] + format_warning + colors['reset'],
        logging.ERROR: colors['bold_red'] + format_error + colors['reset'],
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class FormatterNoColor(logging.Formatter):

    format_debug = "     %(levelname)s: %(message)s (%(filename)s)"
    format_info = "%(message)s"
    format_banner = "=========  %(message)s"
    format_warning = "%(levelname)s: %(message)s (%(filename)s)"
    format_error = "%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: format_debug,
        logging.INFO: format_info,
        25: format_banner,
        logging.WARNING: format_warning,
        logging.ERROR: format_error,
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


def init_logger(lverbose,logfile):

    if lverbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # prepare logfile name
    logfile = os.path.basename(logfile)
    logfile = logfile.replace('.py','.log')

    # logs are alway written to logs directory
    logfile = os.path.join('logs',logfile)

    log.setLevel(level)

    logging.addLevelName(25,"BANNER")
    logging.Logger.banner = banner

    ch = logging.StreamHandler()
    ch.setLevel(level)

    ch.setFormatter(FormatterColor())

    log.addHandler(ch)

    fh = logging.FileHandler(logfile,mode='w')

    fh.setLevel(level)

    fh.setFormatter(FormatterNoColor())

    log.addHandler(fh)

    # shutdown in case of logging.ERROR
    log.addHandler(ShutdownHandler(level=logging.ERROR))
