# standard modules
import os
import shutil
import argparse

# aliased standard modules
import pandas as pd # to evaluate

# modules of sanity checker
import paths
import utils
import logger_config

# standalone imports
from logger_config import log
from test_config import get_config_of_current_test

def add_line_descr_f(exp,f_exp_descr):
    '''
    Add line for exp exp in file f_exp_descr

    :param exp: new exp name
    :param f_exp_descr: file in which the new line has to be added
    :return:
    '''

    log.info('Adding line {} in the file {}:'.format(exp,f_exp_descr))

    # open file in dataframe
    if not os.path.isfile(f_exp_descr):
        # create dataframe
        cols_exp_descr_f = ['Experiment name',\
                            'Platform',\
                            'OS',\
                            'Compiler (with version)',\
                            'Optimisation level (-OX)',\
                            '-fast-transcendentals (y/n)',\
                            '-no-prec-sqrt (y/n)',\
                            '-no-prec-div (y/n)',\
                            'Date of experiment (month yyyy)']
        pd.DataFrame(columns=cols_exp_descr_f)
    else:
        df_exp_descr = pd.read_csv(f_exp_descr, sep=';')
        #TODO: check if file is not corrupted

    # collect information from user
    log.banner('Please give the following informations about your experiment')
    dict_line = {'Experiment name' : exp}
    for col_name in df_exp_descr.keys():

        # experiment nbame is exp
        if col_name == 'Experiment name' :
            continue
        # ask the user for other info
        dict_line[col_name] = input('{} : '.format(col_name))

   # amend the information if needed
    while True:
        # new dataframe containing new line for exp
        df_exp_descr_new = df_exp_descr.append(dict_line, ignore_index=True)

        log.banner ('Here is the content of the description file including your new experiment.')
        log.info(df_exp_descr_new)
        answ_chg = input('Is the new file right ? (y/n/abort).\n'
                         'If you type n, you will be able to change column values\n'
                         'If you type abort, the process of adding the experiment {} to the reference is stoped.\n'
                         '(y/n/abort) : '
                         ''.format(exp))
        if answ_chg.upper() == 'Y' :
            # save new file
            df_exp_descr_new.to_csv(f_exp_descr,sep=';',index=False)

            # get out of the loop
            return False

        elif answ_chg.upper() == 'N' :
            answ_col = input('Which column field you want to change ? ')

            if answ_col in df_exp_descr.keys():
                dict_line[answ_col] = input('{} : '.format(answ_col))
            else:
                log.warning('{} not in columns!'.format(answ_col))
                log.info('Columns are {}\n'.format(list(df_exp_descr.columns)))

        elif answ_chg.upper() == 'ABORT' :
            exit()
#            return False

    return()

def main(exp, \
         tests,\
         p_stages=paths.p_stages, \
         p_ref_csv_files = paths.p_ref_csv_files, \
         lverbose=False):

    '''
 Interface for adding the csv file containing the annual global means of the experiment [exp] located in p_stages into the reference pool p_ref_csv_files.

 C. Siegenthaler, C2SM 2020-07

    '''

    log.banner('Start add_exp_to_ref for experiment {}'.format(exp))

    # initialisation
    new_branch_name = 'test_add_{}'.format(exp)
    files_to_commit = []

    for test in tests:
        test_cfg = get_config_of_current_test(test)
        csv_file = utils.clean_path(p_stages,'test_postproc_{}_{}.csv'.format(test_cfg.name,exp))

        filename_in_ref_dir = '{}_{}.csv'.format(test_cfg.ref_name,exp)
        place_for_reference = os.path.join(p_ref_csv_files,test,filename_in_ref_dir)

        log.debug('Copy {} to {}'.format(csv_file,place_for_reference))
        shutil.copy(csv_file,place_for_reference)
        files_to_commit.append(place_for_reference)

    # fill up file 'Exps_description.csv'
    f_exp_descr = os.path.join(p_ref_csv_files,'Exps_description.csv')
    add_line_descr_f(exp=exp,f_exp_descr=f_exp_descr)
    files_to_commit.append(f_exp_descr)

    os.chdir(paths.rootdir)

    # checkout new branch
    log.info('Create and checkout new branch {}'.format(new_branch_name))
    git_cmd = 'git checkout -B {}'.format(new_branch_name)
    utils.shell_cmd(git_cmd,py_routine='add_exp_to_ref.py')

    for file in files_to_commit:
        git_cmd = 'git add {}'.format(file)
        log.debug(git_cmd)
        utils.shell_cmd(git_cmd, py_routine=__name__)


    # commit files: Exps_description.csv and csv file of each test
    log.debug('Commit files {}'.format(files_to_commit))
    commit_message = input('Please type your commit message :')
    git_cmd = 'git commit -m "{}"'.format(commit_message)
    utils.shell_cmd(git_cmd, py_routine=__name__)

    # Finish
    log.info('Files are added in the new branch: {} in your local git repository.\n'
          'To add the file in the official repository, Please perform the following steps:\n'
          '1. Push the new branch into the official repo:\n'
          '   git push --set-upstream origin {}\n'
          '2. On the Open Web interface (GitHub) , open a Pull Request.\n'
          '3. In the Pull Request, attach the relevant files in {} (for example Welch test result and different figures).'
          ''.format(new_branch_name,new_branch_name,p_stages))

    log.banner('End add_exp_to_ref for experiment {}'.format(exp))
    return()

if __name__ == '__main__':
    # parsing arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--exp','-e', dest = 'exp',\
                            required = True,\
                            help = 'exp to add')

    parser.add_argument('--p_stages', dest='p_stages', \
                            default=paths.p_stages, \
                            help='relative or absolute path of the csv files of the testresults')

    parser.add_argument('--p_ref_csv_files', dest='p_ref_csv_files', \
                        default = paths.p_ref_csv_files,\
                        help=' path to the pool of csv files, one per reference experiment')

    parser.add_argument('--tests','-t', dest='tests', \
                           default=['welchstest','pattern_correlation','emissions'], \
                           nargs='+',\
                           help = 'Tests to add to reference pool')

    parser.add_argument('--verbose','-v', dest='lverbose', \
                           action='store_true', \
                           help = 'Debug output')

    args = parser.parse_args()

    # init logger
    logger_config.init_logger(args.lverbose)

    # make all paths from user to absolute paths
    args.p_stages = utils.abs_path(args.p_stages)
    args.p_ref_csv_files = utils.abs_path(args.p_ref_csv_files)

    main(exp=args.exp, \
         tests=args.tests,\
         p_stages=args.p_stages, \
         p_ref_csv_files=args.p_ref_csv_files, \
         lverbose=args.lverbose)

