# standard modules
import logging
import sys
import os
import subprocess

# modules of sanity checker
import lib.paths as paths

# standalone imports
from lib.logger_config import log

'''
Module providing useful functions. It contains:

    - clean_path: make a clean paths from a path and filename

    - abs_path: convert path passed as argument into absolute

    - determine_actions_for_data_processing:
            Check what stages of data-processing
            already took place, determine relevant
            actions still to do

    - shell_cmd: execute shell-command with subprocess.Popen

    - derive_arguments_for_add_exp_to_ref: create argument list to run
            add_exp_to_ref.py as main manually

    - rel_path: convert path to relative path with respect to paths.rootdir

C.Siegenthaler 2019
J.Jucker 12.2020
'''


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

def abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        path = os.path.abspath(path)
        return path

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

        if (not os.path.isfile(test_specific_csv) or \
            lforce or \
            actions['standard_postproc'][test]):

            action_needed = True
        else:
            action_needed = False

        actions['test_postproc'][test] = action_needed

    log.debug('actions: {}'.format(actions))

    return(actions)


def shell_cmd(cmd,py_routine,lowarn=False):

    """ 
    Send shell command through subprocess.Popen and returns a string 
    containing the cmd output

    lowarn = True -> only a warning is written, no exit (To use with caution!)
    """

    # send cmd to be executed
    p = subprocess.Popen(cmd, shell=True, \
                         stdout = subprocess.PIPE, stderr = subprocess.PIPE, \
                         universal_newlines=True)

    # gets the output of the cmd
    out, err = p.communicate()

    # initailisation output status
    out_status = 0
    # check if cmd was executed properly
    if p.returncode != 0:
        log.debug("{} (shell_cmd): ERROR in the command: \n {}".format(py_routine,cmd))
        if lowarn :
            log.warning("Error returned: \n {}".format(err))
            out_status = 1
        else:
            log.error("Error returned: {}".format(err))

    return(out_status,str(out))

def derive_arguments_for_add_exp_to_ref(exp,tests, p_stages, p_ref_csv_files):

    args = '--exp {} '.format(exp)

    args += '--tests '
    for test in tests:
        args += '{} '.format(test)

    p_stages = rel_path(p_stages)
    args += '--p_stages {} '.format(p_stages)

    p_ref_csv_files = rel_path(p_ref_csv_files)
    args += '--p_ref_csv_files {} '.format(p_ref_csv_files)

    return args

def rel_path(path):
    path = os.path.relpath(path,paths.rootdir)
    return path
