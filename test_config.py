# standalone imports
from logger_config import log
from color import Style

def get_config_of_current_test(testname):
    if testname == 'welchstest':
        config = welchs()
    elif testname == 'emissions':
        config = emission()
    elif testname == 'pattern_correlation':
        config = pattern()
    else:
        log.error('Test {} does not exist'.format(testname))

    return config

class welchs:
    def __init__(self):
        self.name = 'welchstest'
        self.ref_name = 'glob_means'
        self.metric = 'p-value [%]'
        self.metric_threshold = [\
                               threshold_prop('very low', 1, 'DarkRed'), \
                               threshold_prop('low', 5, 'Red'), \
                               threshold_prop('middle', 10, 'Orange'), \
                               threshold_prop('high', 100, 'Green')]
class emission:
    def __init__(self):
        self.name = 'emissions'
        self.ref_name = 'emis'
        self.metric = 'relative deviation [%]'
        self.metric_threshold = [\
                               threshold_prop('high', 1e-19, 'Green'),\
                               threshold_prop('middle', 1e-16, 'Orange'), \
                               threshold_prop('low', 1e-13, 'Red'), \
                               threshold_prop('very low', 1e-10, 'DarkRed')]

class pattern:
    def __init__(self):
        self.name = 'pattern_correlation'
        self.ref_name = 'fldcor'
        self.metric = 'R^2'
        self.metric_threshold =  [\
                               threshold_prop('high', 1e-19, 'Green'),\
                               threshold_prop('middle', 1e-16, 'Orange'), \
                               threshold_prop('low', 1e-13, 'Red'), \
                               threshold_prop('very low', 1e-10, 'DarkRed')]

class threshold_prop:
    '''Properties linked to the metrics threshold'''

    def __init__(self, lev, metric_threshold, color_var):

        # defining color text
        dict_col = {'Red': Style.RED, 'DarkRed': Style.RED_HIGHL, 'Orange':Style.ORANGE,'Green' : Style.GREEN}

        try:
            self.col_txt = dict_col[color_var]
        except KeyError:
            log.warning('No text color associated with {} --> setting to BLACK'.format(color_var))
            self.col_txt = Style.BLACK

        # other properties
        self.level = lev
        self.p_thresh = metric_threshold
        self.col_graph = color_var
