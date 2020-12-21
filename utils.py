import logging
import sys
import os


log = logging.getLogger()

def clean_path(dir, file):
    '''
    returns a clean path from a dir and file

    used to check if all files
    exist, if not exit programme
    '''

    clean_path = os.path.join(dir, file)
    try:
        f = open(clean_path)
    except FileNotFoundError:
        log.error('{} not found'.format(file), exc_info=True)

    f.close()

    return clean_path

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    green = "\033[32m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_debug = "     %(levelname)s: %(message)s (%(filename)s)"
    format_info = "%(message)s"
    format_banner = "=========  %(message)s ========="
    format_warning = "%(levelname)s: %(message)s (%(filename)s)"
    format_error = "%(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format_debug + reset,
        logging.INFO: grey + format_info + reset,
        25: green + format_banner + reset,
        logging.WARNING: yellow + format_warning + reset,
        logging.ERROR: bold_red + format_error + reset,
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
           # Yes, logger takes its '*args' as 'args'.
           self._log(25, message, args, **kws) 

def init_logger(lverbose):

    # create logger with 'spam_application'
    #logger = logging.getLogger('Test')

    if lverbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log.setLevel(level)

    logging.addLevelName(25,"BANNER")
    logging.Logger.banner = banner

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level)

    ch.setFormatter(CustomFormatter())

    log.addHandler(ch)

    # shutdown in case of logging.ERROR
    log.addHandler(ShutdownHandler(level=logging.ERROR)) 


if __name__ == '__main__':

    # create logger with 'spam_application'
    logger = logging.getLogger('Test')

    level = logging.DEBUG

    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)
    logger.addHandler(ShutdownHandler(level=logging.ERROR)) 
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
