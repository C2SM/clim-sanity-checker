# Script to test sanity of a an HAMMOZ run
# C.Siegenthaler, 2019



import process_data
import argparse
import os
import pandas as pd
import numpy as np
import glob
from scipy import stats
import plot_mean_std as plt
import add_exp_to_ref
import paths                 # the file paths.py is written by paths_init.py
import utils
from utils import log

class style():
    '''define colors for output on terminal'''

    BLACK = lambda x: '\033[30m' + str(x)
    RED = lambda x: '\033[31m' + str(x)
    GREEN = lambda x: '\033[32m' + str(x)
    ORANGE = lambda x: '\033[93m' + str(x)
    RED_HIGHL = lambda x: '\u001b[41m' + str(x)
    RESET = lambda x: '\033[0m' + str(x)

class pval_thr_prop:
    '''Properties linked to the p-value threshold'''

    def __init__(self, lev, p_threshold, color_var):

        # defining color text
        dict_col = {'Red': style.RED, 'DarkRed': style.RED_HIGHL, 'Orange':style.ORANGE,'Green' : style.GREEN}

        if color_var in dict_col.keys():
            self.col_txt = dict_col[color_var]
        else:
            print('Warning no text color associated with {}'.format(color_var))
            self.col_txt = style.RESET

        # other properties
        self.level = lev
        self.p_thresh = p_threshold
        self.col_txt = dict_col[color_var]
        self.col_graph = color_var

class table_ref:
    def __init__(self, file_summary):
        # tabs in the excel file
        tabs_table = {'exp' : 'Experiment description', \
                      'globmean' : 'Global annual mean', \
                      'patcor' : 'Pattern correlation', \
                      'emi' : 'Emissions'}
        # assigne one key per tab
        for sh_name, tab in tabs_table.items():
            self.__dict__[sh_name] = pd.read_excel(file_summary, tab)

        # keep track of the tab names
        self.tabs = tabs_table

def df_drop_inplace(df,col_list):
    ''' Drop columns in col_list if the column exists '''

    # list of columns to drop (which are present in df
    list_to_drop = [col for col in col_list if col in df.keys()]

    # drop list of existing columns
    df.drop(labels=list_to_drop,axis=1,inplace=True)

    return

def create_big_df(list_csv_files, filename_csv=''):
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
            print('Warning csv file is not a file : {}'.format(fexp))

    if len(filename_csv) > 0 :
        df_tot.to_csv(filename_csv, sep = ';')

    return df_tot

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
        df_result.to_csv(filename_student_test, sep = ',')

    return (df_result)

def sort_level_metric(df_result, metric_thresholds, metric):
    '''add column in df_results filled with level of p-value'''

    # define out the level of Warning
    bins = [t.p_thresh for t in metric_thresholds]
    bins = [0] + bins
    metric_levels = [t.level for t in metric_thresholds]

    # sort each variable into bins in function of its p-values
    df_result['level'] = pd.cut(df_result[metric], bins, labels=metric_levels)

    return df_result

def print_warning_color(df_result, metric_thresholds, metric):
    ''' Print database df_warning with the color col_warn'''

    # dataframe containing only variables a warning has to be printed
    df_warning = df_result[df_result['level'] != metric_thresholds[-1].level]

    print('----------------------------------------------------------------------------------------------------------')

    if df_warning.size > 0:

        print('WARNING :: the following variables give low {} : \n'.format(metric))

        # for each level of warning, print the dataframe
        for metric_lev in metric_thresholds[:-1]:

            # dataframe containing only this level of warning
            df_print_warn = df_warning[df_warning.level == metric_lev.level]

            # print
            if df_print_warn.size > 0:
                print(style.RESET('{} {} '.format(metric_lev.level.upper(),metric)))
                #print(metric_lev.col_txt(df_print_warn.drop(metric,axis=1)))
                print(metric_lev.col_txt(df_print_warn))
                print(style.RESET('\n'))
    else:
        print(style.GREEN('The experiment is fine. No {} under {} ').format(metric,metric_thresholds[1].p_thresh))
        print(style.RESET('\n'))

    print('----------------------------------------------------------------------------------------------------------')

    return

def add_color_df_result(df_result,pval_thresholds):
    '''Add the color for the graph to the df_result datframe'''

    df_result['col-graph'] = np.nan
    for pval_lev in pval_thresholds:
        df_result.loc[df_result.level == pval_lev.level,'col-graph'] = pval_lev.col_graph

    return df_result

def run(new_exp, \
       p_raw_files, \
       raw_f_subfold,\
       p_ref_csv_files, \
       wrk_dir, \
       p_out_new_exp,\
       f_vars_to_extract, \
       tests, \
       spinup, \
       lclean, \
       lverbose):

    # init logger
    utils.init_logger(lverbose)

    log.banner('Start sanity checker')

    # go in workdir
    os.makedirs(wrk_dir,exist_ok=True)
    os.chdir((wrk_dir))
    log.info('Working directory is {}'.format(wrk_dir))

    # new experiment to test
    # -------------------------------------------------------------

    # get data new exp in dataframe
    actions = utils.determine_actions_for_data_processing(new_exp,tests,p_out_new_exp,wrk_dir,lclean)

    # create dataframe out of raw data
    df_timeser_exp,df_pattern_exp,df_emis  = process_data.main(new_exp, \
                           actions, \
                           tests, \
                           spinup,\
                           p_raw_files=p_raw_files, \
                           p_wrkdir=wrk_dir, \
                           p_output=p_out_new_exp, \
                           raw_f_subfold=raw_f_subfold,\
                           f_vars_to_extract=f_vars_to_extract)

    df_timeser_exp['exp'] = new_exp
    #df_pattern_exp['exp'] = new_exp

    full_p_f_vars = os.path.join(paths.p_f_vars_proc,f_vars_to_extract)
    vars_to_analyse = list(pd.read_csv(full_p_f_vars, sep=',')['var'].values)

    # list of paths to all csv files
    p_csv_files = glob.glob(os.path.join(p_ref_csv_files,'emis_*csv'))
    if len(p_csv_files) == 0:
        print('ERROR : santity_test.py : No reference files found in {}\n EXITING'.format(p_ref_csv_files))
        exit()
    print(p_csv_files)

    df_ref_emis = pd.read_csv(p_csv_files[0], sep=';')
    df_ref_emis = df_ref_emis[vars_to_analyse]

    print(df_ref_emis)
    print(df_emis)


    df_emis['diff'] = df_emis - df_ref_emis

    emis_metric = 'deviation'

    # sort variables from their p-value
    devi_thresholds = [pval_thr_prop('very low', 1e-15, 'DarkRed'), \
                       pval_thr_prop('low', 1e-16, 'Red'), \
                       pval_thr_prop('middle', 1e-17, 'Orange'), \
                       pval_thr_prop('high', 0, 'Green')]
    df_result_pattern = sort_level_metric(df_test, devi_thresholds,pattern_metric)
    print_warning_color(df_result_pattern, rcor_thresholds, pattern_metric)


    # pattern correlation test
    pattern_metric = 'R_squared'

    df_pattern_exp = df_pattern_exp[vars_to_analyse]
    print(df_pattern_exp)
    df_test = pd.DataFrame()
    df_test['variable'] = df_pattern_exp.columns.values
    df_test[pattern_metric] = df_pattern_exp.loc[0].values

    # sort variables from their p-value
    rcor_thresholds = [pval_thr_prop('very low', 0.94, 'DarkRed'), \
                       pval_thr_prop('low', 0.95, 'Red'), \
                       pval_thr_prop('middle', 0.97, 'Orange'), \
                       pval_thr_prop('high', 1, 'Green')]
    df_result_pattern = sort_level_metric(df_test, rcor_thresholds,pattern_metric)
    print_warning_color(df_result_pattern, rcor_thresholds, pattern_metric)




    ######################################################################
    ############## PACK INTO PART FOR WELCHS-TEST #######################

    # data of reference pool
    # ---------------------------------------------------------------
    # get experiments of reference folder (in the fiuture, download from Git)
    # download files into p_csv_files

    # list of paths to all csv files
    p_csv_files = glob.glob(os.path.join(p_ref_csv_files,'glob_means_*csv'))
    if len(p_csv_files) == 0:
        print('ERROR : santity_test.py : No reference files found in {}\n EXITING'.format(p_ref_csv_files))
        exit()

    # create big dataframe containing all reference exps
    df_ref = create_big_df(list_csv_files=p_csv_files)

    # Exclude all the non-desired variables (1) var from file, 2) exp)
    full_p_f_vars = os.path.join(paths.p_f_vars_proc,f_vars_to_extract)
    vars_to_analyse = list(pd.read_csv(full_p_f_vars, sep=',')['var'].values)
    vars_to_analyse.append('exp')
    df_ref = df_ref[vars_to_analyse]
    df_new_exp = df_timeser_exp[vars_to_analyse]

    # Perform Welch's t-test for each variable
    # ----------------------------------------------------------------
    file_result_welche = os.path.join(p_out_new_exp,'result_welchs_test_{}.csv'.format(new_exp))
    df_result = welch_test_all_var(df_a=df_ref, df_b=df_new_exp,filename_student_test=file_result_welche)
    df_result['p-value [%]'] = df_result['p-value']*100.

    timeser_metric = 'p-value [%]'
    # sort variables from their p-value
    pval_thresholds = [pval_thr_prop('very low', 1, 'DarkRed'), \
                       pval_thr_prop('low', 5, 'Red'), \
                       pval_thr_prop('middle', 99, 'Orange'), \
                       pval_thr_prop('high', 100, 'Green')]
    df_result = sort_level_metric(df_result, pval_thresholds,timeser_metric)

    # print infos
    # -------------------------------------------------------------------
    print ('Welch test on each variable for the the comparison between the references and the new experiment {}:'.format(new_exp))

    # print warnings for small p-values
    print_warning_color(df_result, pval_thresholds,timeser_metric)

    # print info output file
    print('To see the whole table containing p-values, please the file:{}'.format(file_result_welche))
    print()

    # plot
    # -------------------------------------------------------------------
    # add color of the plot in the dataframe
    df_result = add_color_df_result(df_result,pval_thresholds)
    plt.plt_var(df_ref.append(df_new_exp,sort=False), new_exp, df_result)

    ############## END PACK INTO PART FOR WELCHS-TEST #######################

    ######## PATTERN CORRELATION TEST 



    # Add experiment to the reference pool
    #--------------------------------------------------------------------
    print('-------------------------------------------------------------------------')
    asw = input('If you are happy with this experiment, do you want to add it to the reference pool ? (yes/[No])\n')
    if (asw.strip().upper() == 'YES') or (asw.strip().upper() == 'Y'):
        add_exp_to_ref.main(new_exp, \
                            p_out_new_exp = p_out_new_exp, \
                            p_ref_csv_files = p_ref_csv_files)
    else:
        print('The experiment {} is NOT added to the reference pool \n'.format(new_exp))
        print('If you want to add the experiment {} to the reference pool later on, type the following line when you are ready:\n \
                          add_exp_to_ref --new_exp {}'.format(new_exp, new_exp))
        print('EXITING')

    print ('### Sanity test finished ###')

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--exp','-e', dest = 'exp',\
                            required = True,\
                            default = 'euler_REF_10y', \
                            help = 'exp to proceed')

    parser.add_argument('--p_raw_files', dest = 'p_raw_files',\
                            default = paths.p_raw_files,\
                            help = 'absolute path to raw files (default: {})'.format(paths.p_raw_files))

    parser.add_argument('--p_output', dest='p_output', \
                            default=paths.p_ref_csv_files, \
                            help='absolute path to write csv files (default: {})'.format(paths.p_ref_csv_files))

    parser.add_argument('--p_stages', dest='p_stages', \
                            default=paths.p_stages, \
                            help='relative or absolute path to write csv files of the testresults (default: {})'.format(paths.p_out_new_exp))

    parser.add_argument('--raw_f_subfold', dest= 'raw_f_subfold',\
                            default='',\
                            help='Subfolder where the raw data are ')

    parser.add_argument('--wrkdir','-w', dest= 'wrk_dir',\
                            default=paths.p_wrkdir,\
                            help='relative or absolute path to working directory (default: {}'.format(paths.p_wrkdir))

    parser.add_argument('--f_vars_to_extract',dest='f_vars_to_extract',\
                           default='vars_echam-hammoz.csv',\
                           help = 'File containing variables to anaylse')

    parser.add_argument('--verbose','-v', dest='lverbose', \
                           action='store_true', \
                           help = 'Debug output')

    parser.add_argument('--clean','-c', dest='lclean', \
                           action='store_true', \
                           help = 'Redo all processing steps')

    parser.add_argument('--spinup', dest='spinup', \
                           type=int, \
                           default=3,\
                           help='Do not consider first month of the data due to model spinup (default: 3)')

    parser.add_argument('--tests','-t', dest='tests', \
                           default=['welchstest','pattern_correlation','emissions'], \
                           nargs='+',\
                           help = 'Tests to apply on your data (default: welchstest pattern_correlation emissions')


    args = parser.parse_args()

    run(new_exp = args.exp, \
           p_raw_files = args.p_raw_files, \
           raw_f_subfold = args.raw_f_subfold,\
           p_ref_csv_files = args.p_output, \
           wrk_dir = args.wrk_dir, \
           p_out_new_exp = args.p_out_new_exp,\
           f_vars_to_extract = args.f_vars_to_extract, \
           tests = args.tests, \
           spinup = args.spinup, \
           lclean = args.lclean, \
           lverbose = args.lverbose)
