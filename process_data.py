#
import os
import xarray as xr
import paths                    # the file paths.py is written by paths_init.py
import pandas as pd
import std_avrg_using_cdo
import pattern_correlation
import argparse
import shell_utilities as su          # file shell_utilities.py part of the distribution
import standard_postproc
from utils import log
import utils

def timeser_proc_nc_to_df(exp, \
        filename, \
        p_stages):

    '''
Read netcdf file containing global mean values timeseries and transforms into dataframe.


Arguments: 
exp               = experiment name
filename          = filename (incl path) to the global means time series file

C. Siegenthaler, C2SM(ETHZ) , 2019-10
 
    '''

    test = 'welchstest'
    timeser_filename = 'test_postproc_{}_{}.nc'.format(test,exp)
    cdo_cmd = 'cdo -L yearmean -fldmean -vertsum {} {}'.format(filename,timeser_filename) 
    su.shell_cmd (cdo_cmd,py_routine=__name__)
    
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
        p_stages           = paths.p_ref_csv_files):

    '''
Read netcdf file containing global mean values timeseries and transforms into dataframe.


Arguments: 
exp               = experiment name
filename          = filename (incl path) to the global means time series file

C. Siegenthaler, C2SM(ETHZ) , 2019-10
 
    '''
    
    test = 'pattern_correlation'
    pattern_filename = 'test_postproc_intermediate_{}_{}.nc'.format(test,exp)

    field_correlation_filename = 'test_proc_{}_{}.nc'.format(test,exp)

    cdo_cmd = 'cdo -L timmean -yearmean -vertsum {} {}'.format(filename,pattern_filename) 
    su.shell_cmd (cdo_cmd,py_routine=__name__)
    # list of variables in the timeserie netcdf file to drop (not to put into the dataframe)
    vars_to_drop = []

    # print info
    log.info('Compute field-correlation between {} and {} (reference)'.format(pattern_filename,reference))

    cdo_cmd = 'cdo -L -sqr -fldcor {} {} {}'.format(pattern_filename,reference,field_correlation_filename) 
    su.shell_cmd (cdo_cmd,py_routine=__name__)
    
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
Read netcdf file containing global mean values timeseries and transforms into dataframe.


Arguments: 
exp               = experiment name
filename          = filename (incl path) to the global means time series file

C. Siegenthaler, C2SM(ETHZ) , 2019-10
 
    '''
    
    test = 'emissions'
    emis_filename = 'test_postproc_{}_{}.nc'.format(test,exp)

    cdo_cmd = 'cdo -L timmean -fldmean -vertsum {} {}'.format(filename,emis_filename) 
    su.shell_cmd (cdo_cmd,py_routine=__name__)
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
         f_vars_to_extract):

    '''
Process exp 
    '''
    log.banner('Start standard-postprocessing')

    processed_netcdf_filename = {}
    for test in tests:
        if (actions['standard_postproc'][test]): 
            processed_netcdf_filename[test] = standard_postproc.main(exp, \
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
        if (actions['test_postproc'][test]):
            # transforming netcdf timeseries into csv file
            df_timeser = timeser_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_stages     = p_stages)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_timeser_csv = os.path.join(p_stages, 'test_postproc_{}_{}.csv'.format(test,exp))
            df_timeser = pd.read_csv(f_timeser_csv, sep=';')
    else:
        log.warning("Skip Welch's-Test")
        df_timeser = None

    if 'emissions' in tests:
        test = 'emissions'
        if (actions['test_postproc'][test]):
            df_emis = emis_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_stages     = p_stages)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_emis_csv = os.path.join(p_stages, 'test_postproc_{}_{}.csv'.format(test,exp))
            df_emis = pd.read_csv(f_emis_csv, sep=';')
    else:
        log.warning('Skip emission test')
        df_emis = None

    if 'pattern_correlation' in tests:
        test = 'pattern_correlation'
        if (actions['test_postproc'][test]):
            test = 'pattern_correlation'
            reference ='/scratch/juckerj/sanity_check/ref_data/test_postproc_pattern_correlation_euler_REF_10y.nc'
            df_pattern = pattern_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_stages     = p_stages, \
                reference = reference)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_pattern_csv = os.path.join(p_stages, 'test_postproc_{}_{}.csv'.format(test,exp))
            df_pattern = pd.read_csv(f_pattern_csv, sep=';')
    else:
        log.warning('Skip pattern correlation test')
        df_pattern = None

    log.banner('End conversion from NetCDF to dataframe')

    return(df_timeser,df_pattern,df_emis)


if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--exp','-e', dest = 'exp',\
                            required = True,\
                            default = 'euler_REF_10y', \
                            help = 'exp to proceed')

    parser.add_argument('--p_raw_files', dest = 'p_raw_files',\
                            default = paths.p_raw_files,\
                            help = 'absolute path to raw files (default: {})'.format(paths.p_raw_files))

    parser.add_argument('--p_stages', dest='p_stages', \
                            default=paths.p_stages, \
                            help='relative path to write csv files of the different processing steps (default: {})'.format(paths.p_stages))

    parser.add_argument('--raw_f_subfold', dest= 'raw_f_subfold',\
                            default='',\
                            help='Subfolder where the raw data are ')

    parser.add_argument('--wrkdir','-w', dest= 'wrk_dir',\
                            default=paths.p_wrkdir,\
                            help='relative or absolute path to working directory (default: {}'.format(paths.p_wrkdir))

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
                           help='Do not consider first month of the data due to model spinup (default: 3)')

    parser.add_argument('--tests','-t', dest='tests', \
                           default=['welchstest','pattern_correlation','emissions'], \
                           nargs='+',\
                           help = 'Tests to apply on your data (default: welchstest pattern_correlation emissions')

    args = parser.parse_args()

    utils.init_logger(args.lverbose)

    log.banner('Start execute {} as main()'.format(__file__))

    args.wrk_dir = utils.abs_path(args.wrk_dir)
    args.p_stages = utils.abs_path(args.p_stages)

    actions = utils.determine_actions_for_data_processing(args.exp,args.tests,args.p_stages,args.lclean)

    # go in workdir
    os.makedirs(args.p_stages,exist_ok=True)
    os.makedirs(args.wrk_dir,exist_ok=True)
    os.chdir((args.wrk_dir))
    log.info('Current directory is {}'.format(args.wrk_dir))


    main(exp=args.exp,\
         actions = actions, \
         tests = args.tests, \
         spinup = args.spinup,\
         p_raw_files=args.p_raw_files,\
         raw_f_subfold=args.raw_f_subfold,\
         p_stages=args.p_stages,\
         f_vars_to_extract=args.f_vars_to_extract)

    log.banner('End execute {} as main()'.format(__file__))
