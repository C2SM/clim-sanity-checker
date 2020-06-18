# Script to perform the standard time and spatial averaging
# C.Siegenthaler, C2SM, 2010-06

from config_path import paths_cscs as paths
import begin
import os
import glob
import pandas  as pd
import subprocess
import numpy as np

def variables_to_extract(vars_in_expr):
    '''
Return the list of variables to extract from the list of expressions which contain the variables
    '''
    
    # split expressions around =,-,*,/ and remove numbers
    for op_str in ['*','-','+','/'] :
        vars_in_expr = [s.strip('().') for sl in vars_in_expr for s in sl.split(op_str)]
   
    # only keep unique entries
    vars_uniq = list(np.unique(np.array(vars_in_expr)))
   
    # keep only meaningfull variables, multiplication factors are removed, '' and 'e' (rest for 8e1) are removed
    variables = []
    for v in vars_uniq:
        if len(v.strip('1234567890.'))>1: 
            variables.append(v)
    
    return(variables) 

def shell_cmd(cmd,lowarn=False):
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


def run(exp,\
        p_raw_files       = paths.p_raw_files,\
        p_time_serie      = paths.p_ref_time_serie,\
        wrk_dir           = paths.wrk_dir):

     # create output folders if not existing
     for fold in [p_time_serie,wrk_dir]:
         if not os.path.isdir(fold):
             os.mkdir(fold)

     # get variables to process:
     df_vars = pd.read_csv('./variables_to_process_echam.csv', sep=',')

     # define expressions
     df_vars['expr'] = df_vars['var'] + '=' + df_vars['formula']

     # go in workdir
     if len(wrk_dir) > 0 :
         os.chdir((wrk_dir))

     # name of output file
     ofile_tot = os.path.join(p_time_serie,'timeser_{}.nc'.format(exp))

     # initialisation
     files_error = []      # list files giving error
     files_proceed = []    # list of files where data are collected     
 
     # loop over output stream
     for f in df_vars['file'].unique():

         # extract all lines with file f
         df_file = df_vars[df_vars.file==f]     
         
         # list all available files in p_raw_files/exp/Raw which have stream f
         ifiles = glob.glob(os.path.join(p_raw_files,exp,'Raw','{}_*{}.nc'.format(exp,f)))

         # sort files in chronoligcal order (this will be needed for doing yearmean properly)
         ifiles.sort()

         # output file for stream f
         ofile_f = '{}_{}.nc'.format(exp,f)

         # variables to extract form netcdf files (this is needed for optimization)
         variables = variables_to_extract(vars_in_expr=df_file.formula.values)
        
         # Extract variables needed from big files 
         print('Extract variables from {} files:'.format(f))
         # initialization
         tmp_selvar_files = []       # list to store the ifiles
         for ifile in ifiles: 
             # basename of ifile
             ifile_bsn = os.path.basename(ifile)
             print(ifile_bsn)
             tmp_selvar_file = 'tmp_extract_{}'.format(ifile_bsn) 
             
             cdo_cmd = 'cdo selvar,{} {} {}'.format(','.join(variables),ifile,tmp_selvar_file) 
             out_status,out_mess = shell_cmd(cdo_cmd,lowarn=True)
             
             if out_status == 0:
                 tmp_selvar_files.append(tmp_selvar_file)
             else:
                 files_error.append(ifile_bsn)
         
         # Merge all the monthlyfiles together 
         print('Copy and average {} files'.format(f))
         tmp_merged = 'tmp_{}.nc'.format(f)
         cdo_cmd = 'cdo -copy {} {}'.format(' '.join(tmp_selvar_files), tmp_merged)
         shell_cmd (cdo_cmd)

         # time average and compute needed variables
         print('Compute final variables for file : {}'.format(f))
         if os.path.isfile(ofile_f):
             os.remove(ofile_f)
         expr_str = ';'.join((df_file.expr.values))
         cdo_cmd = 'cdo yearmean -fldmean -setctomiss,-9e+33 -expr,"{}" {} {}'.format(expr_str,tmp_merged,ofile_f) 
         shell_cmd (cdo_cmd)

         # keep trace of output file per stream
         files_proceed.append(ofile_f)

         # cleaning


               
     # merge all stream files
     cdo_cmd = 'cdo merge {} {}'.format(' '.join(files_proceed),ofile_tot)
     shell_cmd(cdo_cmd)

     # Finishing
     print('Finished : files with a problem: {}'.format(','.join(files_error)))
     print ('Script std_avrg_using_cdo.py finished. Output here : {}'.format(ofile_tot))
