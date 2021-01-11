# standard modules
import os
import argparse
import glob

# aliased standard modules
import pandas as pd
import xarray as xr
import numpy as np

# modules of sanity checker
import lib.paths as paths
import lib.utils as utils
import lib.logger_config as logger_config

# standalone imports
from lib.logger_config import log

'''
Module doing all the postprocessing of the raw model output.
It can be called as a function from sanity_check.py or directly
as main().
It contains:

    - variables_to_extract: Infer list of variables to extract from 
            the list of expressions which contain the variables

    - standard_postproc: process all raw data into a global annual mean netCDF,
            used in all test, contains hack for already processed data (ECHAM only)

    - timeser_proc_nc_to_df: Read netCDF with global mean values timeseries
            and transform it into dataframe, used for Welch's-Test

    - pattern_proc_nc_to_df: Read netCDF with global mean values and transform
            it into dataframe, used for pattern correlation test

    - emis_proc_nc_to_df: Read netCDF with global mean values and transform
            it into datafram, used for emissions test

    - main: main function that combines the different processing steps
            
            Help: python process_data.py --help

C.Siegenthaler 2019 (C2SM)
J.Jucker 12.2020 (C2SM)

'''

def download_ref_to_stages_if_required(f_pattern_ref,p_stages,f_vars_to_extract,test):
        
        # no ref-file passed as argument of process_data
        if f_pattern_ref == paths.rootdir:
            log.info('Download reference file from ftp-server')

            filename_ftp_link = f_vars_to_extract.replace('.csv','.txt').replace('vars_','ftp_')
            path_to_ftp_link = os.path.join(paths.p_f_vars_proc,test)
            file_with_ftp_link = utils.clean_path(path_to_ftp_link,filename_ftp_link)

            output_file = os.path.join(p_stages,'ftp_ref_pattern.nc')

            cmd = 'wget --input-file={} --output-document={}'.format(file_with_ftp_link,output_file)
            log.debug('ftp-command: {}'.format(cmd))
            utils.shell_cmd(cmd,py_routine=__name__)

            f_pattern_ref = output_file

        else:
            log.info('Using user-defined reference file for test {}'.format(test))

        return f_pattern_ref


def variables_to_extract(vars_in_expr):
    
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

def standard_postproc(exp,\
        test, \
        spinup,\
        p_raw_files, \
        raw_f_subfold,\
        p_stages, \
        f_vars_to_extract):

    '''
Perfom standard post-processing using cdo 

Arguments: 
    exp               = experiment name
    test              = name of current test to process data
    spinup            = number of files (from begining of simulation) to ignore du to model spinup
    p_raw_files       = path to raw model output
    raw_f_subfold     = subfolder in p_raw_files with model output [p_raw_files]/[raw_f_subfold]
    p_stages:         = directory where processing steps are stored
   f_vars_to_extract : csv file containg the variables to proceed

returns: 
   time series of yearly global means for variables defined in f_vars_to_extract 
    '''

    log.info('Postprocess data using CDO for test {}'.format(test))

    # check that exp is defined
    if exp is None :
        log.error('Experiment is not defined.\n exp = {}'.format(exp))

    # get variables to process:
    p_test_vars_proc = os.path.join(paths.p_f_vars_proc, test)
    full_p_f_vars = utils.clean_path(p_test_vars_proc,f_vars_to_extract)
    df_vars = pd.read_csv(full_p_f_vars, sep=',')

    # define expressions
    df_vars['expr'] = df_vars['var'] + '=' + df_vars['formula']

    # name of output file
    ofile_tot = os.path.join(p_stages,'standard_postproc_{}_{}.nc'.format(test,exp))

    # initialisation
    files_error = []      # list files giving error
    files_proceed = []    # list of files where data are collected 
    
    # sometimes data is stored in a folder called Raw
    p_raw_folder = os.path.join(p_raw_files,exp,raw_f_subfold)

    # SPECIAL CASE, echam specific : 
    # if the folder containing the Raw files have been deleted, but folder 'Data' contains already global annual means 
    if not os.path.isdir(p_raw_folder):
        log.warning('The folder containing the raw data has been deleted : {}'.format(p_raw_folder))
        p_altern_timeser_fold = os.path.join(p_raw_files,exp,'Data')
        if test == 'welchstest':
            time_series_altern_fold = glob.glob(os.path.join(p_altern_timeser_fold,'timeser_daint_*.nc'))
        if test == 'pattern_correlation':
            time_series_altern_fold = glob.glob(os.path.join(p_altern_timeser_fold,'multi_annual_means_*.nc'))
        if test == 'emissions':
            time_series_altern_fold = glob.glob(os.path.join(p_altern_timeser_fold,'emi_*.nc'))

        if len(time_series_altern_fold) < 1:
            log.error('Could not find files in alternative directory {}'.format(time_series_altern_fold))
        else:
            log.info('The alternative folder has been found instead: {}'.format(p_altern_timeser_fold))

            if len(time_series_altern_fold) == 1: index_ts = 0
            if len(time_series_altern_fold) > 1:

               for (i, item) in enumerate(time_series_altern_fold):
                   print(i, item)
               index_ts = int(input('Please type the index of the file to use (negative means none of them) : '))

            # If index positive, copy the time serie and exit
            if index_ts >= 0 :
               log.info('File used : {}'.format(time_series_altern_fold[index_ts]))
               cdo_cmd = 'cdo -chname,CDNC,burden_CDNC -chname,ICNC,burden_ICNC -chname,SCF,SCRE -chname,LCF,LCRE {} {}'.format(time_series_altern_fold[index_ts],ofile_tot)
               utils.shell_cmd (cdo_cmd,py_routine=__name__)

               # convert netCDF to dataframe, therefore skip next processing step
               if test == 'welchstest':
                   timeser_proc_nc_to_df(\
                                         exp,\
                                         ofile_tot,\
                                         p_stages,\
                                         already_a_timeseries=True)
                   skip_next_steps = True
               else:
                   skip_next_steps = False

               return(ofile_tot,skip_next_steps)

    # NORMAL CASE
    else:
        log.info('Analyse files in : {}'.format(p_raw_folder))

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
            log.warning('No raw files found for stream {} at address : \n {}'.format(stream,final_p_raw_files))         
            
        # sort files in chronoligcal order (this will be needed for doing yearmean properly)
        ifiles.sort()

        # remove spin-up files
        log.info('Remove first {} months of data due to model spinup'.format(spinup)) 
        ifiles = ifiles[int(spinup):]

        # output file for stream f
        ofile_str = '{}_{}.nc'.format(exp,stream)

        # variables to extract form netcdf files (this is needed for optimization)
        variables = variables_to_extract(vars_in_expr=df_file.formula.values)
       
        # Extract variables needed from big files 
        log.info('Extract variables from file: {}'.format(stream))
        
        # initialization
        tmp_selvar_files = []       # list to store the ifiles
        
        for ifile in ifiles: 
            # basename of ifile
            ifile_bsn = os.path.basename(ifile)
            log.debug('File {}'.format(ifile_bsn))
            tmp_selvar_file = 'tmp_extract_{}'.format(ifile_bsn) 
            
            cdo_cmd = 'cdo selvar,{} {} {}'.format(','.join(variables),ifile,tmp_selvar_file) 
            out_status,out_mess = utils.shell_cmd(cdo_cmd,py_routine=__name__,lowarn=True)
            
            if out_status == 0:
                tmp_selvar_files.append(tmp_selvar_file)
            else:
                files_error.append(ifile_bsn)
        
        # Merge all the monthly files together 
        log.info('Copy {} files'.format(stream))
        tmp_merged = 'tmp_{}_{}.nc'.format(exp,stream)
        if os.path.isfile(tmp_merged):
            os.remove(tmp_merged)

        cdo_cmd = 'cdo -copy {} {}'.format(' '.join(tmp_selvar_files), tmp_merged)
        utils.shell_cmd (cdo_cmd,py_routine=__name__)

        # compute needed variables
        log.info('Compute variables for file : {}'.format(stream))
        if os.path.isfile(ofile_str):
            os.remove(ofile_str)
        expr_str = ';'.join((df_file.expr.values))
        cdo_cmd = 'cdo -L -setctomiss,-9e+33 -expr,"{}" {} {}'.format(expr_str,tmp_merged,ofile_str) 
        utils.shell_cmd (cdo_cmd,py_routine=__name__)

        # keep trace of output file per stream
        files_proceed.append(ofile_str)

        # cleaning
        [os.remove(f) for f in tmp_selvar_files]
        os.remove(tmp_merged)
              
    # merge all stream files
    if os.path.isfile(ofile_tot):
        os.remove(ofile_tot)
    cdo_cmd = 'cdo merge {} {}'.format(' '.join(files_proceed),ofile_tot)
    utils.shell_cmd(cdo_cmd,py_routine=__name__)

    [os.remove(f) for f in files_proceed]

    # Finish
    if len(files_error) != 0 : 
        log.warning('Files with a problem: {}'.format(','.join(files_error)))

    log.info('Postprocess data using CDO for test {} finished. \n Output here : {}'.format(test,ofile_tot))

    # return name of output file
    return(ofile_tot,False)

def timeser_proc_nc_to_df(exp, \
        filename, \
        p_stages, \
        already_a_timeseries= False):

    '''
Arguments: 
    exp               = experiment name
    filename          = filename of the global means time series file
    p_stages:         = directory where processing steps are stored

returns:
    dataframe with processed data
    '''

    test = 'welchstest'

    if already_a_timeseries == False:
        timeser_filename = 'test_postproc_{}_{}.nc'.format(test,exp)
        cdo_cmd = 'cdo -L yearmean -fldmean -vertsum {} {}'.format(filename,timeser_filename) 
        utils.shell_cmd (cdo_cmd,py_routine=__name__)
    else:
        log.debug('Skipping CDO-processing step')
        timeser_filename = filename
    
    # list of variables in the timeserie netcdf file to drop (not to put into the dataframe)
    vars_to_drop = []

    log.info('Processing netCDF: {}'.format(timeser_filename))

    # open dataset
    data = xr.open_dataset(timeser_filename)

    # Delete variables
    # useless variable time_bnds
    if ('time_bnds' in data.keys()):
        data = data.drop('time_bnds')
    # 3D vars
    if len(vars_to_drop)>0:
        data.drop(labels = vars_to_drop)

    # removed degenerated dimensions
    data = data.squeeze(drop = True)

    # transforms into dataframe
    df_data = data.to_dataframe()

    # export in a file
    os.makedirs(p_stages, exist_ok=True)
    csv_filename = os.path.join(p_stages,'test_postproc_{}_{}.csv'.format(test,exp))
    df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
    log.info('CSV file can be found here: {}'.format(csv_filename))     

    log.info('Finished {} for file {}'.format(__name__,timeser_filename))
    
    return(df_data)

def pattern_proc_nc_to_df(exp, \
        filename, \
        reference, \
        p_stages):

    '''
Arguments: 
    exp               = experiment name
    filename          = filename to the global means file
    reference:        = filename to the reference
    p_stages:         = directory where processing steps are stored

returns:
    dataframe with processed data
    '''
    
    test = 'pattern_correlation'
    pattern_filename = 'test_postproc_intermediate_{}_{}.nc'.format(test,exp)

    field_correlation_filename = 'test_proc_{}_{}.nc'.format(test,exp)

    cdo_cmd = 'cdo -L timmean -yearmean -vertsum {} {}'.format(filename,pattern_filename) 
    utils.shell_cmd (cdo_cmd,py_routine=__name__)
    # list of variables in the timeserie netcdf file to drop (not to put into the dataframe)
    vars_to_drop = []

    log.info('Compute field-correlation between {} and {} (reference)'.format(pattern_filename,reference))

    cdo_cmd = 'cdo -L -sqr -fldcor {} {} {}'.format(pattern_filename,reference,field_correlation_filename) 
    utils.shell_cmd (cdo_cmd,py_routine=__name__)
    
    # open dataset
    data = xr.open_dataset(field_correlation_filename)

    # Delete variables
    # useless variable time_bnds
    if ('time_bnds' in data.keys()):
        data = data.drop('time_bnds')
    # 3D vars
    if len(vars_to_drop)>0:
        data.drop(labels = vars_to_drop)

    # transforms into dataframe
    df_data = data.to_dataframe()

    os.makedirs(p_stages, exist_ok=True)
    csv_filename = os.path.join(p_stages,'test_postproc_{}_{}.csv'.format(test,exp))
    df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
    log.info('CSV file can be found here: {}'.format(csv_filename))     

    log.info('Finished {} for file {}'.format(__name__,field_correlation_filename))

    return(df_data)

def emis_proc_nc_to_df(exp, \
        filename, \
        p_stages):

    '''
Arguments: 
    exp               = experiment name
    filename          = filename to the global means file
    p_stages:         = directory where processing steps are stored

returns:
    dataframe with processed data
    '''
    
    test = 'emissions'
    emis_filename = 'test_postproc_{}_{}.nc'.format(test,exp)

    cdo_cmd = 'cdo -L timmean -fldmean -vertsum {} {}'.format(filename,emis_filename) 
    utils.shell_cmd (cdo_cmd,py_routine=__name__)
    # list of variables in the timeserie netcdf file to drop (not to put into the dataframe)
    vars_to_drop = []

    log.info('Processing netCDF: {}'.format(emis_filename))

    # open dataset
    data = xr.open_dataset(emis_filename)

    # Delete variables
    # useless variable time_bnds
    if ('time_bnds' in data.keys()):
        data = data.drop('time_bnds')
    # 3D vars
    if len(vars_to_drop)>0:
        data.drop(labels = vars_to_drop)

    # transforms into dataframe
    df_data = data.to_dataframe()

    # export in a file
    os.makedirs(p_stages, exist_ok=True)
    csv_filename = os.path.join(p_stages,'test_postproc_{}_{}.csv'.format(test,exp))
    df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
    log.info('CSV file can be found here: {}'.format(csv_filename))     
    
    log.info('Finished {} for file {}'.format(__name__,emis_filename))

    return(df_data)


def main(exp,\
         actions, \
         tests,\
         spinup,\
         p_raw_files,\
         p_stages,\
         raw_f_subfold,\
         f_vars_to_extract,\
         f_pattern_ref):

    log.banner('Start standard-postprocessing')

    results_data_processing = {}
    processed_netcdf_filename = {}
    skip_next_step = {}

    # init in case standard_postproc is skipped
    for test in tests:
        skip_next_step[test] = False

    for test in tests:
        if (actions['standard_postproc'][test]): 
            processed_netcdf_filename[test], skip_next_step[test]= standard_postproc(exp, \
                                        test = test, \
                                        spinup = spinup, \
                                        p_raw_files       = p_raw_files, \
                                        raw_f_subfold     = raw_f_subfold,\
                                        p_stages = p_stages, \
                                        f_vars_to_extract = f_vars_to_extract)
        else:
            log.info('Data already processed for test {}'.format(test))
            processed_netcdf_filename[test] = utils.clean_path(p_stages, 'standard_postproc_{}_{}.nc'.format(test,exp))

    log.banner('End standard-postprocessing')

    log.banner('Start conversion from NetCDF to dataframe')

    if 'welchstest' in tests:

        test = 'welchstest'

        if (actions['test_postproc'][test] and not skip_next_step[test]):
            # transforming netcdf timeseries into csv file
            results_data_processing[test] = timeser_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_stages     = p_stages)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_csv = os.path.join(p_stages, 'test_postproc_{}_{}.csv'.format(test,exp))
            results_data_processing[test] = pd.read_csv(f_csv, sep=';')
    else:
        log.warning("Skip Welch's-Test")

    if 'emissions' in tests:

        test = 'emissions'

        if (actions['test_postproc'][test] and not skip_next_step[test]):
            results_data_processing[test] = emis_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_stages     = p_stages)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_csv = os.path.join(p_stages, 'test_postproc_{}_{}.csv'.format(test,exp))
            results_data_processing[test] = pd.read_csv(f_csv, sep=';')
    else:
        log.warning('Skip emission test')

    if 'pattern_correlation' in tests:

        test = 'pattern_correlation'

        if (actions['test_postproc'][test] and not skip_next_step[test]):
            test = 'pattern_correlation'

            f_pattern_ref = download_ref_to_stages_if_required(f_pattern_ref,p_stages,f_vars_to_extract,test)

            results_data_processing[test] = pattern_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_stages     = p_stages, \
                reference = f_pattern_ref)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_csv = os.path.join(p_stages, 'test_postproc_{}_{}.csv'.format(test,exp))
            results_data_processing[test] = pd.read_csv(f_csv, sep=';')
    else:
        log.warning('Skip pattern correlation test')

    log.banner('End conversion from NetCDF to dataframe')

    return(results_data_processing)


if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--exp','-e', dest = 'exp',\
                            required = True,\
                            default = 'euler_REF_10y', \
                            help = 'exp to proceed')

    parser.add_argument('--p_raw_files', dest = 'p_raw_files',\
                            default = paths.p_raw_files,\
                            help = 'absolute path to raw files')

    parser.add_argument('--p_stages', dest='p_stages', \
                            default=paths.p_stages, \
                            help='relative path to write csv files of the different processing steps')

    parser.add_argument('--raw_f_subfold', dest= 'raw_f_subfold',\
                            default='',\
                            help='Subfolder where the raw data are ')

    parser.add_argument('--wrkdir','-w', dest= 'wrk_dir',\
                            default=paths.p_wrkdir,\
                            help='relative or absolute path to working directory')

    parser.add_argument('--f_vars_to_extract',dest='f_vars_to_extract',\
                           default='vars_echam-hammoz.csv',\
                           help = 'File containing variables to anaylse')

    parser.add_argument('--verbose','-v', dest='lverbose', \
                           action='store_true', \
                           help = 'Debug output')

    parser.add_argument('--clean','-c', dest='lclean', \
                           action='store_true', \
                           help = 'Redo all processing steps')

    parser.add_argument('--spinup', dest='spinup', \
                           type=int, \
                           default=3,\
                           help='Do not consider first month of the data due to model spinup')

    parser.add_argument('--tests','-t', dest='tests', \
                           default=['welchstest','pattern_correlation','emissions'], \
                           nargs='+',\
                           help = 'Tests to apply on your data')

    parser.add_argument('--f_pattern_ref', dest='f_pattern_ref', \
                           default='', \
                           help = 'Absolute or relative path to reference netCDF for spatial correlation tests')

    args = parser.parse_args()

    logger_config.init_logger(args.lverbose)

    log.banner('Start execute {} as main()'.format(__file__))

    # make all paths from user to absolute paths
    args.wrk_dir = utils.abs_path(args.wrk_dir)
    args.p_stages = utils.abs_path(args.p_stages)
    args.f_pattern_ref = utils.abs_path(args.f_pattern_ref)

    # data processing takes a while, check that no step is done twice
    actions = utils.determine_actions_for_data_processing(args.exp,args.tests,args.p_stages,args.lclean)

    # create directories
    os.makedirs(args.p_stages,exist_ok=True)
    os.makedirs(args.wrk_dir,exist_ok=True)

    # go to working directory
    os.chdir((args.wrk_dir))
    log.info('Current directory is {}'.format(args.wrk_dir))


    main(exp=args.exp,\
         actions = actions, \
         tests = args.tests, \
         spinup = args.spinup,\
         p_raw_files=args.p_raw_files,\
         raw_f_subfold=args.raw_f_subfold,\
         p_stages=args.p_stages,\
         f_vars_to_extract=args.f_vars_to_extract,\
         f_pattern_ref=args.f_pattern_ref)

    log.banner('End execute {} as main()'.format(__file__))
