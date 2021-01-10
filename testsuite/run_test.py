import os
import subprocess

def test_run_sucess():
    cmd = 'python paths_init.py -pr testsuite/data --p_stages /scratch/snx3000/juckerj/sanity_test/stages_home/ --p_wrkdir /scratch/snx3000/juckerj/sanity_test/wrkdir_home/'
    status, _ =shell_cmd(cmd,py_routine=__name__)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python sanity_test.py -v -e emi_test -t emissions --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_emi_test.csv -c -ts'

    status, _ =shell_cmd(cmd,py_routine=__name__)

    assert status == 0, 'sanity_test.py failed'

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
    print(str(out))
    print(str(err))

    return p.returncode,(str(out)+str(err))

