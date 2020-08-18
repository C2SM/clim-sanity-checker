# Script to add new experiment called [new_exp] in pthe refernce pool

import os
import shutil
import argparse
import pandas as pd
import paths                          # the file paths.py is written by paths_init.py
import shell_utilities as su          # file shell_utilities.py part of the distribution

def add_line_descr_f(new_exp,f_exp_descr):
    '''
    Add line for exp new_exp in file f_exp_descr

    :param new_exp: new exp name
    :param f_exp_descr: file in which the new line has to be added
    :return:
    '''

    print('Adding line {} in the file {}:'.format(new_exp,f_exp_descr))

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

    # collect information from user
    print('Please give the following informations about your experiment')
    dict_line = {'Experiment name' : new_exp}
    for col_name in df_exp_descr.keys():

        # experiment nbame is new_exp
        if col_name == 'Experiment name' :
            continue
        # ask the user for other info
        dict_line[col_name] = input('{} : '.format(col_name))

   # amend the information if needed
    while True:
        # new dataframe containing new line for new_exp
        df_exp_descr_new = df_exp_descr.append(dict_line, ignore_index=True)

        print ('Here is the content of the description file including your new experiment.')
        print (df_exp_descr_new)
        answ_chg = input('Is the new file right ? (y/n/abort).\n'
                         'If you type n, you will be able to change column values\n'
                         'If you type abort, the process of adding the experiment {} to the reference is stoped.\n'
                         '(y/n/abort) : '
                         ''.format(new_exp))
        if answ_chg.upper() == 'Y' :
            # save new file
            df_exp_descr_new.to_csv(f_exp_descr,sep=';')

            # get out of the loop
            return False
        elif answ_chg.upper() == 'N' :
            answ_col = input('Which column field you want to change ? ')

            if answ_col in df_exp_descr.keys():
                dict_line[answ_col] = input('{} : '.format(answ_col))
            else:
                print ('{} not in columns names !!!'.format(answ_col))
        elif answ_chg.upper() == 'ABORT' :
            exit()
#            return False

    return()

def main(new_exp, \
         p_out_new_exp=paths.p_out_new_exp, \
         p_ref_csv_files = paths.p_ref_csv_files, \
         lverbose=False):

    '''
 Interface for adding the csv file containing the annual global means of the experiment [new_exp] located in p_out_new_exp into the reference pool p_ref_csv_files.

 C. Siegenthaler, C2SM 2020-07

    '''

    if lverbose: print('Begin add_exp_to_ref for experiment {}'.format(new_exp))

    # initialisation
    new_branch_name = 'test_add_{}'.format(new_exp)

    # checkout new branch
    print('Create and checkout new branch {}'.format(new_branch_name))
    git_cmd = 'git checkout -B {}'.format(new_branch_name)
    su.shell_cmd(git_cmd,py_routine='add_exp_to_ref.py')

    # mv file
    filename = 'glob_means_{}.csv'.format(new_exp)
    old_path =os.path.join(p_out_new_exp,filename)
    new_path = os.path.join(p_ref_csv_files,filename)
    if os.path.isfile((old_path)):
        shutil.move(old_path,new_path)
    else:
        print('WARNING : add_exp_to_ref.py : The file {} does not exist'.format(old_path))

    # fill up file 'Exps_description.csv'
    f_exp_descr = os.path.join(p_ref_csv_files,'Exps_description.csv')
    add_line_descr_f(new_exp=new_exp,f_exp_descr=f_exp_descr)

    # add updated Exps_description.csv and csv file of global annual means of new_exp into git
    os.chdir(paths.p_scripts)                  # ensure we are in the script dir
    rel_path_new_f = os.path.relpath(new_path, paths.p_scripts)
    git_cmd = 'git add {} {}'.format(rel_path_new_f,f_exp_descr)
    su.shell_cmd(git_cmd, py_routine='add_exp_to_ref.py')

    # commit 2 files: Exps_description.csv and csv file of global annual means of new_exp
    print('Commit files {} and {} in git.'.format(rel_path_new_f,f_exp_descr))
    commit_message = input('Please type your commit message :')
    git_cmd = 'git commit -m "{}"'.format(commit_message)
    su.shell_cmd(git_cmd, py_routine='add_exp_to_ref.py')

    # Finish
    print('-------------------------------------------------------------------------\n'
          'File rel_path_new_f is added in the new branch : {} in your local git repository.\n'
          'To add the file in the official repository, Please perform the following steps:\n'
          '1. Push the new branch into the official repo:\n'
          '   git push --set-upstream origin {}\n'
          '2. On the Open Web interface (GitLab) , open a Pool Request.\n'
          '3. In the Pool Request, attach the relevant files in {} (for example Welch test result and different figures).'
          ''.format(new_branch_name,new_branch_name,p_out_new_exp))
    return()

if __name__ == '__main__':
    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--new_exp', '-n', dest='new_exp', \
                        required=True, \
                        help='exp to add')

    parser.add_argument('--p_out_new_exp',dest='p_out_new_exp',\
                        default=paths.p_out_new_exp,\
                        help = 'path to the folder for the result of new experiment to analyse (default : ./results_new_exp)')

    parser.add_argument('--p_ref_csv_files', dest='p_ref_csv_files', \
                        default = paths.p_ref_csv_files,\
                        help=' path to the pool of csv files, one per reference experiment (default: ./ref/echam-hammoz)')


    parser.add_argument('--lverbose', dest='lverbose', action='store_true')

    args = parser.parse_args()

    main(new_exp=args.new_exp, \
         p_out_new_exp=args.p_out_new_exp, \
         p_ref_csv_files=args.p_ref_csv_files, \
         lverbose=args.lverbose)

