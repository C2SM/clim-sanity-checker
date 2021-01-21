# standalone imports
from lib.logger_config import log
from lib.color import Style

'''
Module providing classes and functions related to the tests. It contains:

    - get_config_of_current_test: return configuration 
        of the test matching the string passed as argument

    - class WelchsTest: define properties of Welch's t-test

    - class EmissionsTest: define properties of emission test

    - class FldcorTest: define properties of field correlation test

    - class RmseTest: define properties of 
        normalize root mean square error test

    - class threshold_prop: contains the properties of a testmetric 
        e.g. color, threshold or significance level

J.Jucker 12.2020 (C2SM)

'''


def get_config_of_current_test(testname):
    if testname == 'welch':
        config = WelchsTest()
    elif testname == 'emi':
        config = EmissionsTest()
    elif testname == 'fldcor':
        config = FldcorTest()
    elif testname == 'rmse':
        config = RmseTest()
    else:
        log.error('Test {} does not exist'.format(testname))

    return config


class WelchsTest:
    def __init__(self):
        self.name = 'welch'
        self.ref_name = 'glob_means'
        self.metric = 'p-value [%]'
        self.metric_threshold = [
            threshold_prop('very low', 1, 'DarkRed'),
            threshold_prop('low', 5, 'Red'),
            threshold_prop('middle', 10, 'Orange'),
            threshold_prop('high', 100, 'Green')]


class EmissionsTest:
    def __init__(self):
        self.name = 'emi'
        self.ref_name = 'emis'
        self.metric = 'relative deviation [%]'
        self.metric_threshold = [
            threshold_prop('high', 0.01, 'Green'),
            threshold_prop('middle', 0.1, 'Orange'),
            threshold_prop('low', 1, 'Red'),
            threshold_prop('very low', 10, 'DarkRed')]


class FldcorTest:
    def __init__(self):
        self.name = 'pattern_correlation'
        self.ref_name = 'fldcor'
        self.metric = 'R^2'
        self.metric_threshold = [
            threshold_prop('very low', 0.97, 'DarkRed'),
            threshold_prop('low', 0.98, 'Red'),
            threshold_prop('middle', 0.99, 'Orange'),
            threshold_prop('high', 1, 'Green')]


class RmseTest:
    def __init__(self):
        self.name = 'rmse'
        self.ref_name = 'rmse'
        self.metric = 'normalized RMSE'
        self.metric_threshold = [
            threshold_prop('high', 0.01, 'Green'),
            threshold_prop('middle', 0.05, 'Orange'),
            threshold_prop('low', 0.1, 'Red'),
            threshold_prop('very low', 0.2, 'DarkRed')]


class threshold_prop:
    '''Properties linked to the metrics threshold'''

    def __init__(self, lev, metric_threshold, color_var):

        # defining color text
        dict_col = {'Red': Style.RED, 'DarkRed': Style.RED_HIGHL,
                    'Orange':Style.ORANGE,'Green': Style.GREEN}

        try:
            self.col_txt = dict_col[color_var]
        except KeyError:
            log.warning('No text color associated with {} - ' 
                        'setting to BLACK'.format(color_var))
            self.col_txt = Style.BLACK

        # other properties
        self.level = lev
        self.p_thresh = metric_threshold
        self.col_graph = color_var
