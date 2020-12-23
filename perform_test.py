import utils
from scipy import stats
import glob
import pandas as pd
import argparse
import os
from utils import log
import paths
import numpy as np
from color import style

def add_color_df_result(df_result,metric_thresholds):
    '''Add the color for the graph to the df_result datframe'''

    df_result['col-graph'] = np.nan
    for metric_lev in metric_thresholds:
        df_result.loc[df_result.level == metric_lev.level,'col-graph'] = metric_lev.col_graph

    return df_result

def print_warning_color(df_result, metric_thresholds, metric):
    ''' Print database df_warning with the color col_warn'''

    # dataframe containing only variables a warning has to be printed
    df_warning = df_result[df_result['level'] != 'high']
    #import IPython;IPython.embed()

    log.info('----------------------------------------------------------------------------------------------------------')

    if df_warning.size > 0:

        log.warning('The following variables give low {} : \n'.format(metric))

        # for each level of warning, print the dataframe
        for metric_lev in metric_thresholds:
            if metric_lev != 'high':

                # dataframe containing only this level of warning
                df_print_warn = df_warning[df_warning.level == metric_lev.level]

                # print
                if df_print_warn.size > 0:
                    log.info('{} {} '.format(metric_lev.level.upper(),metric))
                    log.info(metric_lev.col_txt(df_print_warn))
    else:
        log.info(style.GREEN('The experiment is fine. No {} under {} \n').format(metric,metric_thresholds[1].p_thresh))

    log.info('----------------------------------------------------------------------------------------------------------')

    return

def sort_level_metric(df_result, metric_thresholds, metric):
    '''add column in df_results filled with level of p-value'''

    # define out the level of Warning
    bins = [t.p_thresh for t in metric_thresholds]

    bins = [-1e-10] + bins


    metric_levels = [t.level for t in metric_thresholds]

    # sort each variable into bins in function of its p-values
    df_result['level'] = pd.cut(df_result[metric], bins, labels=metric_levels)

    return df_result

class threshold_prop:
    '''Properties linked to the metrics threshold'''

    def __init__(self, lev, metric_threshold, color_var):

        # defining color text
        dict_col = {'Red': style.RED, 'DarkRed': style.RED_HIGHL, 'Orange':style.ORANGE,'Green' : style.GREEN}

        try:
            self.col_txt = dict_col[color_var]
        except KeyError:
            log.warning('No text color associated with {} --> setting to BLACK'.format(color_var))
            self.col_txt = style.BLACK

        # other properties
        self.level = lev
        self.p_thresh = metric_threshold
        self.col_graph = color_var

def pattern_correlation_all_var(df_exp):
    '''
    Perform Welch t-test for each variable fo dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :param filename_student_test: filename for writing result of t-test result into a csv file
    :return: result of the student test in a dataframe
    '''

    # initialisation for construction dataframe (much faster to use list than dataframe.append)
    row_list_df = []

    for var in df_exp.keys():
        if 'exp' in var:
            continue
        log.debug("Pattern correlation test for {}".format(var))

        # append results for construction datframe df_result
        dict1 = {'variable' : var, 'R^2' : df_exp[var].iloc[0] }
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, columns=['variable','R^2'] )

    df_result.sort_values(by=['R^2'], inplace=True)

    return (df_result)

def welch_test_all_var(df_a, df_b , filename_student_test = ''):
    '''
    Perform Welch t-test for each variable fo dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :param filename_student_test: filename for writing result of t-test result into a csv file
    :return: result of the student test in a dataframe
    '''

    # initialisation for construction dataframe (much faster to use list than dataframe.append)
    row_list_df = []

    for var in df_b.keys():
        if 'exp' in var:
            continue
        log.debug("Welch's t-test for {}".format(var))
        # Welch's t-test
        t, p = stats.ttest_ind(df_a[var], df_b[var], equal_var = False, nan_policy='omit')

        # append results for construction datframe df_result
        dict1 = {'variable' : var, 't-value' : t , 'p-value' : p}
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, columns=['variable','t-value','p-value'] )

    # sort per p value
    df_result.sort_values(by=['p-value'], inplace=True)

    # if a filename is given, write the student-stest result into the file named filename_student_test
    if len(filename_student_test) > 0 :
        log.info('Write result to {}'.format(filename_student_test))
        df_result.to_csv(filename_student_test, sep = ',')

    return (df_result)

def emissions_all_var(df_exp, df_ref , filename_student_test = ''):
    '''
    Perform Welch t-test for each variable fo dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :param filename_student_test: filename for writing result of t-test result into a csv file
    :return: result of the student test in a dataframe
    '''

    # initialisation for construction dataframe (much faster to use list than dataframe.append)
    row_list_df = []

    for var in df_exp.keys():
        if 'exp' in var:
            continue
        log.debug("Emissions test for {}".format(var))
        deviation = abs(df_exp[var].iloc[0] - df_ref[var].iloc[0])

        # append results for construction datframe df_result
        dict1 = {'variable' : var, 'deviation' : deviation }
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, columns=['variable','deviation'])

    # sort per p value
    df_result.sort_values(by=['deviation'], inplace=True)

    return (df_result)

def create_big_df(ref_names, list_csv_files, filename_csv=''):
    '''
    Create big dataframe form list of csv files
    :param list_csv_files: list of csv files for the big dataframe
    :return: big dataframe containing the whole data
    '''

    # initialise big empty dataframe
    df_tot = pd.DataFrame()

    # create big dataframe
    for fexp in list_csv_files:

        exp = os.path.basename(fexp).rstrip('.csv').replace('glob_means_','')

        # read the csv file
        if os.path.isfile(fexp):
            df_exp = pd.read_csv(fexp, sep=';')
            df_exp['exp'] = exp

            # append dataframe of exp to the total dataframe
            df_tot = df_tot.append(df_exp, sort = False)

        else:
            log.warning('csv file is not a file : {}'.format(fexp))

    if len(filename_csv) > 0 :
        df_tot.to_csv(filename_csv, sep = ';')

    return df_tot

def main(\
         new_exp, \
         results_data_processing,\
         tests, \
         p_stages, \
         p_ref_csv_files,\
         f_vars_to_extract):


    ref_names = {}
    ref_names['welchstest'] = 'glob_means_'
    ref_names['emissions'] = 'emis_'
    ref_names['pattern_correlation'] = 'fldcor_'

    test_metrics ={} 
    test_metrics['welchstest'] = 'p-value [%]'
    test_metrics['emissions'] = 'deviation'
    test_metrics['pattern_correlation'] = 'R^2'

    df_exp = {}
    df_ref = {}
    p_csv_files = {} 
    testresult_csv = {}
    df_result = {}
    metric_threshold = {}

    for test in tests:
        log.info('Prepare references for test {}'.format(test))

        results_data_processing[test]['exp'] = new_exp

        # list of paths to all csv files
        p_csv_files[test] = glob.glob(os.path.join(p_ref_csv_files,test,'{}*csv'.format(ref_names[test])))
        if len(p_csv_files[test]) == 0:
            log.error('No reference files found in {}\n EXITING'.format(p_ref_csv_files))

        log.debug('{} reference(s) found for test {}'.format(len(p_csv_files[test]),test))

        # create big dataframe containing all reference exps
        df_ref[test] = create_big_df(ref_names[test],list_csv_files=p_csv_files[test])

        # Exclude all the non-desired variables (1) var from file, 2) exp)
        full_p_f_vars = os.path.join(paths.p_f_vars_proc,test,f_vars_to_extract)
        vars_to_analyse = list(pd.read_csv(full_p_f_vars, sep=',')['var'].values)
        vars_to_analyse.append('exp')
        df_ref[test] = df_ref[test][vars_to_analyse]
        df_exp[test] = results_data_processing[test][vars_to_analyse]

        log.info('References for test {} prepared'.format(test))

        testresult_csv[test] = os.path.join(p_stages,'result_{}_{}.csv'.format(test,new_exp))

        if test == 'welchstest':
            log.banner('')
            log.banner("Perform Welch's t-test for each variable")
            log.banner('')
            df_result[test] = welch_test_all_var(df_a=df_ref[test], df_b=df_exp[test],filename_student_test=testresult_csv[test])
            df_result[test]['p-value [%]'] = df_result[test]['p-value']*100.

    # sort variables from their p-value
            metric_threshold[test] = [threshold_prop('very low', 1, 'DarkRed'), \
                               threshold_prop('low', 5, 'Red'), \
                               threshold_prop('middle', 10, 'Orange'), \
                               threshold_prop('high', 100, 'Green')]

        if test == 'pattern_correlation':
            log.banner('')
            log.banner("Perform pattern correlation test for each variable")
            log.banner('')
            df_result[test] = pattern_correlation_all_var(df_exp[test])

            metric_threshold[test] = [threshold_prop('very low', 0.97, 'DarkRed'), \
                               threshold_prop('low', 0.99, 'Red'), \
                               threshold_prop('middle', 0.995, 'Orange'), \
                               threshold_prop('high', 1, 'Green')]

        if test == 'emissions':
            log.banner('')
            log.banner("Perform emission test for each variable")
            log.banner('')
            df_result[test] = emissions_all_var(df_exp[test], df_ref[test])

            metric_threshold[test] = [\
                               threshold_prop('high', 0, 'Green'),\
                               threshold_prop('middle', 1e-16, 'Orange'), \
                               threshold_prop('low', 1e-13, 'Red'), \
                               threshold_prop('very low', 1e-10, 'DarkRed')]
        
        df_result[test] = sort_level_metric(df_result[test], metric_threshold[test],test_metrics[test])
        df_result[test] = add_color_df_result(df_result[test],metric_threshold[test])

        print_warning_color(df_result[test], metric_threshold[test],test_metrics[test])

    return df_result,df_ref

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--exp','-e', dest = 'exp',\
                            required = True,\
                            default = 'euler_REF_10y', \
                            help = 'exp to proceed')

    parser.add_argument('--p_stages', dest='p_stages', \
                            default=paths.p_stages, \
                            help='relative or absolute path to write csv files of the testresults (default: {})'.format(paths.p_stages))

    parser.add_argument('--wrkdir','-w', dest= 'wrk_dir',\
                            default=paths.p_wrkdir,\
                            help='relative or absolute path to working directory (default: {}'.format(paths.p_wrkdir))

    parser.add_argument('--p_ref_csv_files', dest= 'p_ref_csv_files',\
                            default=paths.p_ref_csv_files,\
                            help='relative or absolute path to reference files (default: {}'.format(paths.p_ref_csv_files))

    parser.add_argument('--f_vars_to_extract', dest='f_vars_to_extract',\
                           default='vars_echam-hammoz.csv',\
                           help = 'File containing variables to anaylse')

    parser.add_argument('--verbose','-v', dest='lverbose', \
                           action='store_true', \
                           help = 'Debug output')

    parser.add_argument('--clean','-c', dest='lclean', \
                           action='store_true', \
                           help = 'Redo all processing steps')

    parser.add_argument('--tests','-t', dest='tests', \
                           default=['welchstest','pattern_correlation','emissions'], \
                           nargs='+',\
                           help = 'Tests to apply on your data (default: welchstest pattern_correlation emissions')

    args = parser.parse_args()

    utils.init_logger(args.lverbose)

    log.banner('Start execute {} as main()'.format(__file__))

    args.wrk_dir = utils.abs_path(args.wrk_dir)
    args.p_stages = utils.abs_path(args.p_stages)
    args.p_ref_csv_files = utils.abs_path(args.p_ref_csv_files)

    os.chdir((args.wrk_dir))
    log.info('Current directory is {}'.format(args.wrk_dir))

    log.info('Read processed data from csv for...')
    results_data_processing = {}
    for test in args.tests:
        log.info('{}'.format(test))
        f_csv = utils.clean_path(args.p_stages, 'test_postproc_{}_{}.csv'.format(test,args.exp))
        results_data_processing[test] = pd.read_csv(f_csv, sep=';')
    log.info('...done') 

    main(new_exp = args.exp, \
           results_data_processing = results_data_processing, \
           p_stages = args.p_stages,\
           p_ref_csv_files = args.p_ref_csv_files, \
           f_vars_to_extract = args.f_vars_to_extract, \
           tests = args.tests)

    log.banner('End execute {} as main()'.format(__file__))
