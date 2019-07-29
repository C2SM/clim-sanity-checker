import subprocess

def sys_cmd(cmd):
    """ send system command through subprocess. and returns a string containing the cmd output
    """

    # send cmd to be executed
    p = subprocess.Popen(cmd, shell=True, \
                         stdout = subprocess.PIPE, stderr = subprocess.PIPE)
   # p.wait()

    # gets the output of the cmd
    out, err = p.communicate()

    # check if cmd was executed properly
    if p.returncode != 0:
        print("ERROR in the command:")
        print(cmd)
        print ("Error returned:")
        print(err)
        print("Exiting")
        exit()


    return(str(out))
