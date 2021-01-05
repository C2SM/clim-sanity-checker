# Script to test sanity of climate model
# C.Siegenthaler, 2019
# J.Jucker, 2020

# standard modules
import argparse
import os

# aliased standard modules
import pandas as pd # to evaluate

# modules of sanity checker
import add_exp_to_ref
import paths
import utils
import perform_test
import process_data
import logger_config

# aliased modules of sanity checker
import plot_mean_std as plt

# standalone imports
from logger_config import log

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


def run(new_exp, \
       p_raw_files, \
       raw_f_subfold,\
       p_stages, \
       p_ref_csv_files, \
       wrk_dir, \
       f_vars_to_extract, \
       p_emis_ref, \
       f_emis_ref, \
       tests, \
       spinup, \
       lclean, \
       lverbose):

    # init logger
    logger_config.init_logger(lverbose)

    log.banner('Start sanity checker')

    # make all paths from user to absolute paths
    wrk_dir = utils.abs_path(wrk_dir)
    p_stages = utils.abs_path(p_stages)
    p_ref_csv_files = utils.abs_path(p_ref_csv_files)
    p_emis_ref = utils.abs_path(p_emis_ref)

    # create directories
    os.makedirs(p_stages,exist_ok=True)
    os.makedirs(wrk_dir,exist_ok=True)

    # go to working directory
    os.chdir((wrk_dir))
    log.info('Working directory is {}'.format(wrk_dir))


    # data processing takes a while, check that no step is done twice
    actions = utils.determine_actions_for_data_processing(new_exp,tests,p_stages,lclean)

    # create dataframe out of raw data
    results_data_processing = process_data.main(\
                              new_exp, \
                              actions, \
                              tests, \
                              spinup,\
                              p_raw_files=p_raw_files, \
                              p_stages=p_stages, \
                              raw_f_subfold=raw_f_subfold, \
                              f_vars_to_extract=f_vars_to_extract,\
                              p_emis_ref=p_emis_ref,\
                              f_emis_ref=f_emis_ref)

    results_test, references = perform_test.main(\
                           new_exp, \
                           results_data_processing = results_data_processing, \
                           p_stages=p_stages, \
                           tests= tests, \
                           p_ref_csv_files = p_ref_csv_files,\
                           f_vars_to_extract=f_vars_to_extract)
                                    

    if 'emissions' in tests:
        test = 'emissions'
        plt.plt_emissions(references[test].append(results_data_processing[test],sort=False),new_exp, results_test[test], p_out_new_exp = p_stages)
        log.error('exit')

    if 'pattern_correlation' in tests:
        test = 'pattern_correlation'
        plt.plt_pattern_correlation(references[test].append(results_data_processing[test],sort=False),new_exp, results_test[test], p_out_new_exp = p_stages)

    if 'welchstest' in tests:
        test = 'welchstest'
        plt.plt_welchstest(references[test].append(results_data_processing[test],sort=False), new_exp, results_test[test], p_out_new_exp = p_stages)

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

    log.banner('')
    log.banner ('Sanity test finished')
    log.banner('')

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--exp','-e', dest = 'exp',\
                            required = True,\
                            help = 'exp to proceed')

    parser.add_argument('--p_raw_files', dest = 'p_raw_files',\
                            default = paths.p_raw_files,\
                            help = 'absolute path to raw files')

    parser.add_argument('--p_stages', dest='p_stages', \
                            default=paths.p_stages, \
                            help='relative or absolute path to write csv files of the testresults')

    parser.add_argument('--raw_f_subfold', dest= 'raw_f_subfold',\
                            default='',\
                            help='Subfolder where the raw data are ')

    parser.add_argument('--wrkdir','-w', dest= 'wrk_dir',\
                            default=paths.p_wrkdir,\
                            help='relative or absolute path to working directory')

    parser.add_argument('--p_ref_csv_files', dest= 'p_ref_csv_files',\
                            default=paths.p_ref_csv_files,\
                            help='relative or absolute path to reference files')

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
                           help='Do not consider first month of the data due to model spinup')

    parser.add_argument('--tests','-t', dest='tests', \
                           default=['welchstest','pattern_correlation','emissions'], \
                           nargs='+',\
                           help = 'Tests to apply on your data')

    parser.add_argument('--p_emis_ref', dest='p_emis_ref', \
                           default='', \
                           help = 'Absolute or relative path to reference netCDF for pattern correlation test')

    parser.add_argument('--f_emis_ref', dest='f_emis_ref', \
                           default='', \
                           help = 'Filename of reference netCDF for pattern correlation test')


    args = parser.parse_args()

    run(new_exp = args.exp, \
           p_raw_files = args.p_raw_files, \
           raw_f_subfold = args.raw_f_subfold, \
           wrk_dir = args.wrk_dir, \
           p_stages = args.p_stages,\
           p_ref_csv_files = args.p_ref_csv_files, \
           f_vars_to_extract = args.f_vars_to_extract, \
           p_emis_ref = args.p_emis_ref,\
           f_emis_ref = args.f_emis_ref,\
           tests = args.tests, \
           spinup = args.spinup, \
           lclean = args.lclean, \
           lverbose = args.lverbose)
