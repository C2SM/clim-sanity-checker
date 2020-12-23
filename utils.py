import logging
import sys
import os

from color import colors

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
           # Yes, logger takes its '*args' as 'args'.
           self._log(25, message, args, **kws) 

def init_logger(lverbose):

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

def determine_actions_for_data_processing(exp, tests, p_stages,lforce):

    actions = {'standard_postproc': {},
               'test_postproc': {}
               }

    if lforce:
        log.warning('Redo all processing steps')

    # see if standard-postprocessing is needed
    for test in tests:

        standard_proc_nc = os.path.join(p_stages,'standard_postproc_{}_{}.nc'.format(test,exp))
        if (not os.path.isfile(standard_proc_nc) or lforce):
            action_needed = True
        else:
            action_needed = False

        actions['standard_postproc'][test] = action_needed

        test_specific_csv = os.path.join(p_stages,'test_postproc_{}_{}.csv'.format(test,exp))
        print(test_specific_csv)

        if (not os.path.isfile(test_specific_csv) or \
            lforce or \
            actions['standard_postproc'][test]):

            action_needed = True
        else:
            action_needed = False

        actions['test_postproc'][test] = action_needed

    log.debug('actions: {}'.format(actions))

    return(actions)

def abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        path = os.path.abspath(path)
        return path

if __name__ == '__main__':

    path_to_clean = '../test'
    path_abs = '/scratch/juckerj/'
    test_1 = abs_path(path_to_clean)
    test_2 = abs_path(path_abs)
    print(test_1)
    print(test_2)

