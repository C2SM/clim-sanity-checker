# standard modules
import argparse
import os

# aliased standard modules
import pandas as pd

# modules of sanity checker
import add_exp_to_ref
import lib.paths as paths
import lib.utils as utils
import perform_test
import process_data
import lib.logger_config as logger_config
import lib.test_config as test_config

# aliased modules of sanity checker
import lib.plot_mean_std as plt

# standalone imports
from lib.logger_config import log

'''
Script to test sanity of climate models. It contains:

    - main: process model output, perform tests and plot results,
            each function called by main() can be called itself
            as a main(). Prior to the execution, paths_init.py
            needs to be executed. 
            Note that this script requires user input at some stages,
            so it cannot be run as a batched job.

            Help: python sanity_test.py --help

# C.Siegenthaler, 2019
# J.Jucker, 2020

'''


def main(new_exp,
         p_raw_files,
         raw_f_subfold,
         p_stages,
         p_ref_csv_files,
         wrk_dir,
         f_vars_to_extract,
         f_pattern_ref,
         tests,
         spinup,
         lclean,
         ltestsuite,
         lverbose):

    # init logger
    logger_config.init_logger(lverbose)

    log.banner('Start sanity checker')

    # make all paths from user to absolute paths
    wrk_dir = utils.abs_path(wrk_dir)
    p_stages = utils.abs_path(p_stages)
    p_ref_csv_files = utils.abs_path(p_ref_csv_files)
    f_pattern_ref = utils.abs_path(f_pattern_ref)

    # create directories
    os.makedirs(p_stages,exist_ok=True)
    os.makedirs(wrk_dir,exist_ok=True)

    # go to working directory
    os.chdir((wrk_dir))
    log.info('Working directory is {}'.format(wrk_dir))

    # data processing takes a while, check that no step is done twice
    actions = utils.determine_actions_for_data_processing(new_exp,
                                                          tests,
                                                          p_stages,
                                                          lclean)

    # create dataframe out of raw data
    results_data_processing = process_data.main(
        new_exp,
        actions,
        tests,
        spinup,
        p_raw_files=p_raw_files,
        p_stages=p_stages,
        raw_f_subfold=raw_f_subfold,
        f_vars_to_extract=f_vars_to_extract,
        f_pattern_ref=f_pattern_ref)

    results_test, references = perform_test.main(
        new_exp,
        results_data_processing=results_data_processing,
        p_stages=p_stages,
        tests=tests,
        p_ref_csv_files=p_ref_csv_files,
        ltestsuite=ltestsuite,
        f_vars_to_extract=f_vars_to_extract)

    if 'welch' in tests:
        test = 'welch'
        plt.plt_welchstest(
            references[test].append(results_data_processing[test],
                                    sort=False),
            new_exp,
            results_test[test],
            p_stages=p_stages)

    if not ltestsuite:
        # Add experiment to the reference pool
        #--------------------------------------------------------------------
        log.banner('')
        log.banner('Check results again before adding to reference pool')
        log.banner('')

        for test in tests:
            test_cfg = test_config.get_config_of_current_test(test)
            utils.print_warning_if_testresult_is_bad(
                test,
                results_test[test],
                test_cfg.metric_threshold,test_cfg.metric)

        asw = input('If you are happy with this experiment, '
                    'do you want to add it to the reference pool ?'
                    '(yes/[No])\n')

        if (asw.strip().upper() == 'YES') or (asw.strip().upper() == 'Y'):
            add_exp_to_ref.main(new_exp,
                                tests,
                                p_stages=p_stages,
                                p_ref_csv_files=p_ref_csv_files)
        else:
            args_for_manual_execution = \
                utils.derive_arguments_for_add_exp_to_ref(new_exp, 
                                                          tests, 
                                                          p_stages,
                                                          p_ref_csv_files)

            log.info('The experiment {} is NOT added to '
                     'the reference pool \n'.format(new_exp))
            log.info('If you want to add the experiment {} '
                     'to the reference pool later on, type '
                     'the following line when you are ready:'
                     .format(new_exp, new_exp))

            log.info('')
            log.info('python add_exp_to_ref.py {}'
                     .format(args_for_manual_execution))

    log.banner('')
    log.banner('Sanity test finished')
    log.banner('')


if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--exp','-e', dest='exp',
                        required=True,
                        help='exp to proceed')

    parser.add_argument('--p_raw_files', dest='p_raw_files',
                        default=paths.p_raw_files,
                        help='absolute path to raw files')

    parser.add_argument('--p_stages', dest='p_stages',
                        default=paths.p_stages,
                        help='relative or absolute path '
                        'to write csv files of the testresults')

    parser.add_argument('--raw_f_subfold', dest='raw_f_subfold',
                        default='',
                        help='Subfolder where the raw data are ')

    parser.add_argument('--wrkdir','-w', dest='wrk_dir',
                        default=paths.p_wrkdir,
                        help='relative or absolute path to working directory')

    parser.add_argument('--p_ref_csv_files', dest='p_ref_csv_files',
                        default=paths.p_ref_csv_files,
                        help='relative or absolute path to reference files')

    parser.add_argument('--f_vars_to_extract',dest='f_vars_to_extract',
                        default='vars_echam-hammoz.csv',
                        help='File containing variables to anaylse')

    parser.add_argument('--verbose','-v', dest='lverbose',
                        action='store_true',
                        help='Debug output')

    parser.add_argument('--clean','-c', dest='lclean',
                        action='store_true',
                        help='Redo all processing steps')

    parser.add_argument('--testsuite','-ts', dest='ltestsuite',
                        action='store_true',
                        help='Run of testsuite')

    parser.add_argument('--spinup', dest='spinup',
                        type=int,
                        default=3,
                        help='Do not consider first month '
                        'of the data due to model spinup')

    parser.add_argument('--tests','-t', dest='tests',
                        default=['welch','fldcor','rmse','emi'],
                        nargs='+',
                        help='Tests to apply on your data')

    parser.add_argument('--f_pattern_ref', dest='f_pattern_ref',
                        default='',
                        help='Absolute or relative path to reference '
                        'netCDF for spatial correlation tests')

    args = parser.parse_args()

    main(new_exp=args.exp,
         p_raw_files=args.p_raw_files,
         raw_f_subfold=args.raw_f_subfold,
         wrk_dir=args.wrk_dir,
         p_stages=args.p_stages,
         p_ref_csv_files=args.p_ref_csv_files,
         f_vars_to_extract=args.f_vars_to_extract,
         f_pattern_ref=args.f_pattern_ref,
         tests=args.tests,
         spinup=args.spinup,
         lclean=args.lclean,
         ltestsuite=args.ltestsuite,
         lverbose=args.lverbose)
