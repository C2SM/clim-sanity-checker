import begin
import os
import pandas  as pd
from config_path import paths_cscs as paths
import glob
import subprocess

def shell_cmd(cmd,lowarn=False, out_file=None):
    """ send shell command through subprocess. and returns a string containing the cmd output
        lowarn = True -> only a warning is written, no exit (Tu use with caution!!
        out_file = file to write command output . if None -> no outwriting
    """

    # be sure the file is up to date
    out_file.flush()
    
    if out_file is None:
        # send cmd to be executed
        p = subprocess.Popen(cmd, shell=True, \
                         universal_newlines=True, \
                         stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    else:
        p = subprocess.Popen(cmd, shell=True, \
                         universal_newlines=True,\
                         stdout = out_file, stderr = subprocess.PIPE)
    p.wait()
    out_file.flush()

    # gets the output of the cmd
    out, err = p.communicate()
   
    # initailisation output status
    out_status = 0
    # check if cmd was executed properly
    if p.returncode != 0:
        print("ERROR in the command:")
        print(cmd)
        print ("Error returned:")
        print(err)
        if lowarn :
            out_status = 1
        else:
            print("Exiting")
            exit()


    return(out_status,str(out))


@begin.start

def run(p_raw_files       = paths.p_raw_files,\
        p_time_serie       = paths.p_ref_time_serie, \
        f_vars_to_extract = os.path.join(paths.p_gen,'./variables_to_process_echam.csv'),\
        out_file          = os.path.join(paths.p_gen,'out_diffcdo.txt'),\
        lverbose          = False):

    # get experiments to consider
    exps = os.listdir(p_raw_files)

    # testing procedure -> euler_centos74_i17 is considered to be new exp
    exps.remove('euler_REF_10y_i18')
    
    # delete emi_inpout folder
    exps.remove('emi_input')

    # variables
    df_vars = pd.read_csv(f_vars_to_extract, sep=',')
    selvar = ','.join([s.strip() for s in df_vars['var'].values])

    # open out file
    f = open(out_file, "w")

    # loop over exps
    for iexp, exp in enumerate(exps):

       # print info
       print('Processing experiment: {}'.format(exp))
     
       # file 1 
       filename1 = os.path.join(p_time_serie,'timeser_{}.nc'.format(exp))
       
       if not os.path.isfile(filename1):
           print('FIle do not exist: {} \n Exiting'.format(filename1))
    
       # files 2
       p_old_timeser_fold = os.path.join(p_raw_files,exp,'Data')
       time_series_old = glob.glob(os.path.join(p_old_timeser_fold,'timeser_*.nc'))
       if len(time_series_old) > 0:
             if len(time_series_old) == 1: index_ts = 0
             if len(time_series_old) > 1:
                print('Several files found :')
                for (i, item) in enumerate(time_series_old):
                    print(i, item)
                index_ts = int(input('Please type the index of the file to use (negative means none of them) : '))
             # If index positive, copy the time serie and exit
             if index_ts >= 0 :
                filename2 = time_series_old[index_ts]
                print('File used : {}'.format(filename2))

       # debug
       if lverbose:
           for f in [filename1,filename2]:     
               print('vars in {}'.format(f))
               sh_cmd = 'cdo showvar {}'.format(f)
               os.system(sh_cmd) 
      
       # print name exp
       f.write('{} VS \n{} \n'.format(filename1,filename2))
       f.flush()

       # compare
       sh_cmd = 'cdo diffv -selvar,{} {} -selvar,{} -chname,SCRE,SCF -chname,LCRE,LCF {}'.format(selvar,filename1,selvar,filename2)
       #f.write(shell_cmd(sh_cmd,lowarn=True)[1])
       shell_cmd(sh_cmd,lowarn=True,out_file=f)       

       print('---------------------------------------------------------------------')
       f.write('----------------------------------------------------------------------\n')
       f.flush()

    f.close()
