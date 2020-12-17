import paths                          # the file paths.py is written by paths_init.py
import os
import glob
import pandas  as pd
import shell_utilities as su          # file shell_utilities.py part of the distribution
import numpy as np
import argparse

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

def main(exp,\
        p_raw_files       = paths.p_raw_files,\
        p_time_serie      = paths.p_time_serie,\
        wrk_dir           = paths.p_wrkdir,\
        raw_f_subfold     = '',\
        spinup            = 3,\
        f_vars_to_extract = 'vars_echam-hammoz.csv',\
        lstandard_proc    = True, \
        ltimeser_proc     = True, \
        lpattern_proc     = True, \
        lverbose          = False):

     '''
       Perfom standard post-processing using cdo 
       
       arguments :
           p_raw_files       : path to raw files
           p_time_serie      : path to write output file (time series)
           wrk_dir           : path to working dir
           raw_f_subfold     : Subfolder where the raw data are (eg for echam, raw_f_subfold=Raw and the data are in [p_raw_files]/[exp]/Raw
           spinup            : number of files no to consider (from begining of simulation)
           f_vars_to_extract : csv file containg the variables to proceed
           lverbose          : high verbosity
 
       output: 
           time serie of yearly global means for variables defined in f_vars_to_extract 

      C. Siegenthaler, C2SM , 2020-06
     '''
     # check that exp is defined
     if exp is None :
         print('ERROR: std_avrg_using_cdo.py :Experiment is not defined.\n exp = {}\n EXITING'.format(exp))
         exit()

     # create output folders if not existing
     for fold in [p_time_serie,wrk_dir]:
         if not os.path.isdir(fold):
             os.mkdir(fold)

     # get variables to process:
     full_p_f_vars = os.path.join(paths.p_f_vars_proc,f_vars_to_extract)
     df_vars = pd.read_csv(full_p_f_vars, sep=',')

     # define expressions
     df_vars['expr'] = df_vars['var'] + '=' + df_vars['formula']

     # go in workdir
     if len(wrk_dir) > 0 :
         os.chdir((wrk_dir))

     # name of output file
     ofile_tot = os.path.join(p_time_serie,'standard_postproc_{}.nc'.format(exp))

     # initialisation
     files_error = []      # list files giving error
     files_proceed = []    # list of files where data are collected 
    
     # Special case, echam specific : 
     # if the folder containing the Raw files have been deleted, but folder 'Data' contains already global annual means 
     p_raw_folder = os.path.join(p_raw_files,exp,raw_f_subfold)
     if not os.path.isdir(p_raw_folder):
         print('std_avrg_using_cdo.py : The folder containing the raw data has been deleted : {}'.format(p_raw_folder))
         p_altern_timeser_fold = os.path.join(p_raw_files,exp,'Data')
         time_series_altern_fold = glob.glob(os.path.join(p_altern_timeser_fold,'timeser_*.nc'))
         if len(time_series_altern_fold) > 0:
             print('std_avrg_using_cdo.py : The alternative folder has been found instead: {}'.format(p_altern_timeser_fold))
             if len(time_series_altern_fold) == 1: index_ts = 0
             if len(time_series_altern_fold) > 1:
                for (i, item) in enumerate(time_series_altern_fold):
                    print(i, item)
                index_ts = int(input('Please type the index of the file to use (negative means none of them) : '))
             # If index positive, copy the time serie and exit
             if index_ts >= 0 :
                print('std_avrg_using_cdo.py : File used : {}'.format(time_series_altern_fold[index_ts]))
                cdo_cmd = 'cdo -chname,CDCN,CDNC_burden -chname,ICNC,burden_ICNC -chname,SCF,SCRE -chname,LCF,LCRE {} {}'.format(time_series_altern_fold[index_ts],ofile_tot)
                su.shell_cmd (cdo_cmd,py_routine='std_avrg_using_cdo')
                return(ofile_tot)
     else:
         #print info
         print ('std_avrg_using_cdo.py : Analyse files in : {}'.format(p_raw_folder))

     # loop over output stream
     for stream in df_vars['file'].unique():

         # extract all lines with file f
         df_file = df_vars[df_vars.file==stream]

         # list all available files in p_raw_files/exp/raw_f_subfold which have stream f
         # restart files and {}m.format(stream) e.g. echamm.nc files are not considered
         final_p_raw_files = os.path.join(p_raw_folder,'*_*{}*.nc'.format(stream))
         ifiles = [fn for fn in glob.glob(final_p_raw_files) \
                   if sum([s in os.path.basename(fn) for s in ['stream','{}m'.format(stream)]])==0]
         if len(ifiles)==0 : 
             print('WARNING : no raw files found for stream {} at address : \n {}'.format(stream,final_p_raw_files))         
             
         # sort files in chronoligcal order (this will be needed for doing yearmean properly)
         ifiles.sort()

         # remove spin-up files
         ifiles = ifiles[int(spinup):]

         # output file for stream f
         ofile_str = '{}_{}.nc'.format(exp,stream)

         # variables to extract form netcdf files (this is needed for optimization)
         variables = variables_to_extract(vars_in_expr=df_file.formula.values)
        
         # Extract variables needed from big files 
         print('std_avrg_using_cdo.py : Extract variables from file: {}'.format(stream))
         
         # initialization
         tmp_selvar_files = []       # list to store the ifiles
         
         for ifile in ifiles: 
             # basename of ifile
             ifile_bsn = os.path.basename(ifile)
             if lverbose : print('File {}'.format(ifile_bsn))
             tmp_selvar_file = 'tmp_extract_{}'.format(ifile_bsn) 
             
             cdo_cmd = 'cdo selvar,{} {} {}'.format(','.join(variables),ifile,tmp_selvar_file) 
             out_status,out_mess = su.shell_cmd(cdo_cmd,py_routine='std_avrg_using_cdo',lowarn=True)
             
             if out_status == 0:
                 tmp_selvar_files.append(tmp_selvar_file)
             else:
                 files_error.append(ifile_bsn)
         
         # Merge all the monthly files together 
         print('std_avrg_using_cdo.py : Copy {} files'.format(stream))
         tmp_merged = 'tmp_{}_{}.nc'.format(exp,stream)
         if os.path.isfile(tmp_merged):
             os.remove(tmp_merged)
         cdo_cmd = 'cdo -copy {} {}'.format(' '.join(tmp_selvar_files), tmp_merged)
         su.shell_cmd (cdo_cmd,py_routine='std_avrg_using_cdo')

         # compute needed variables
         print('std_avrg_using_cdo.py : Compute variables for file : {}'.format(stream))
         if os.path.isfile(ofile_str):
             os.remove(ofile_str)
         expr_str = ';'.join((df_file.expr.values))
         cdo_cmd = 'cdo -L -setctomiss,-9e+33 -expr,"{}" {} {}'.format(expr_str,tmp_merged,ofile_str) 
         su.shell_cmd (cdo_cmd,py_routine='std_avrg_using_cdo')

         # keep trace of output file per stream
         files_proceed.append(ofile_str)

         # cleaning
         [os.remove(f) for f in tmp_selvar_files]
         os.remove(tmp_merged)
               
     # merge all stream files
     if os.path.isfile(ofile_tot):
         os.remove(ofile_tot)
     cdo_cmd = 'cdo merge {} {}'.format(' '.join(files_proceed),ofile_tot)
     su.shell_cmd(cdo_cmd,py_routine='std_avrg_using_cdo')

     # Finishing
     print('std_avrg_using_cdo.py : files with a problem: {}'.format(','.join(files_error)))
     print ('Script std_avrg_using_cdo.py finished. Output here : {}'.format(ofile_tot))

     # return name of output file
     return(ofile_tot)

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--exp','-e', dest = 'exp',\
                            required = True,\
                            help = 'exp to proceed')

    parser.add_argument('--p_raw_files', dest = 'p_raw_files',\
                            default = paths.p_raw_files,\
                            help = 'path to raw files')

    parser.add_argument('--p_time_serie', dest = 'p_time_serie',\
                            default = paths.wrk_dir,\
                            help = 'path to write output file')

    parser.add_argument('--wrk_dir', dest = 'wrk_dir',\
                            default = paths.wrk_dir,\
                            help = 'workdir')
   
    parser.add_argument('--raw_f_subfold',dest='raw_f_subfold',\
                            default='',\
                            help='Subfolder where the raw data are (eg for echam, "Raw"')
 
    parser.add_argument('--spinup', dest = 'spinup',\
                            default = 3,\
                            help = 'number of files no to consider (from begining of simulation)')    

    parser.add_argument('--f_vars_to_extract', dest = 'f_vars_to_extract',\
                            default ='vars_echam-hammoz.csv',\
                            help = 'csv file containg the variables to proceed')

    parser.add_argument('--lverbose', dest='lverbose', action='store_true') 
  
    args = parser.parse_args()
    
    main(args.exp,\
         p_raw_files=args.p_raw_files,\
         p_time_serie=args.p_time_serie,\
         wrk_dir=args.wrk_dir,\
         raw_f_subfold=args.raw_f_subfold,\
         spinup=args.spinup,\
         f_vars_to_extract=args.f_vars_to_extract,\
         lbverbose=args.lverbose) 

