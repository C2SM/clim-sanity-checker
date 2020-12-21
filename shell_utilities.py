import subprocess
from utils import log

def shell_cmd(cmd,py_routine,lowarn=False):
    """ send shell command through subprocess. and returns a string containing the cmd output
        lowarn = True -> only a warning is written, no exit (Tu use with caution!!
    """

    # send cmd to be executed
    p = subprocess.Popen(cmd, shell=True, \
                         stdout = subprocess.PIPE, stderr = subprocess.PIPE)
   # p.wait()

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


