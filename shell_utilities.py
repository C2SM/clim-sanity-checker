import subprocess

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
        print("{} (shell_cmd): ERROR in the command:".format(py_routine))
        print(cmd)
        print ("Error returned:")
        print(err)
        if lowarn :
            out_status = 1
        else:
            print("Exiting")
            exit()


    return(out_status,str(out))


