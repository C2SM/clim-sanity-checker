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
        p_output           = paths.p_ref_csv_files, \
        lo_export_csvfile = False):

    '''
Read netcdf file containing global mean values timeseries and transforms into dataframe.


Arguments: 
exp               = experiment name
filename          = filename (incl path) to the global means time series file
p_output          = Definition folder where to write output files (only used if lo_export_csvfile = True)
lo_export_csvfile = if True, export the data into a csv file

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

    log.info('Finished {} for file {}'.format(__name__,timeser_filename))

    # export in a file
    os.makedirs(p_output, exist_ok=True)
    csv_filename = os.path.join(p_output,'test_postproc_{}_{}.csv'.format(test,exp))
    df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
    log.info('CSV file can be found here: {}'.format(csv_filename))     
    
    return(df_data)

def pattern_proc_nc_to_df(exp, \
        filename, \
        reference, \
        p_output           = paths.p_ref_csv_files, \
        lo_export_csvfile = False):

    '''
Read netcdf file containing global mean values timeseries and transforms into dataframe.


Arguments: 
exp               = experiment name
filename          = filename (incl path) to the global means time series file
p_output          = Definition folder where to write output files (only used if lo_export_csvfile = True)
lo_export_csvfile = if True, export the data into a csv file

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

    print('Finished field_correlation for file {}'.format(field_correlation_filename))

    os.makedirs(p_output, exist_ok=True)
    csv_filename = os.path.join(p_output,'test_postproc_{}_{}.csv'.format(test,exp))
    df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
    log.info('CSV file can be found here: {}'.format(csv_filename))     

    return(df_data)

def emis_proc_nc_to_df(exp, \
        filename, \
        p_output           = paths.p_ref_csv_files, \
        lo_export_csvfile = False):

    '''
Read netcdf file containing global mean values timeseries and transforms into dataframe.


Arguments: 
exp               = experiment name
filename          = filename (incl path) to the global means time series file
p_output          = Definition folder where to write output files (only used if lo_export_csvfile = True)
lo_export_csvfile = if True, export the data into a csv file

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

    log.info('Finished {} for file {}'.format(__name__,emis_filename))

    # export in a file
    os.makedirs(p_output, exist_ok=True)
    csv_filename = os.path.join(p_output,'test_postproc_{}_{}.csv'.format(test,exp))
    df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
    log.info('CSV file can be found here: {}'.format(csv_filename))     
    

    return(df_data)


def main(exp,\
         actions, \
         tests,\
         spinup,\
         p_raw_files  = paths.p_raw_files,\
         p_wrkdir = paths.p_wrkdir, \
         p_output     = paths.p_out_new_exp,\
         raw_f_subfold     = '',\
         f_vars_to_extract = 'vars_echam-hammoz.csv',
         lo_export_csvfile = True ):

    '''
Process exp 
    '''
    log.banner('Start standard-postprocessing')
# apply standard postprocessing DONE
    processed_netcdf_filename = {}
    for test in tests:
        if (actions['standard_postproc'][test]): 
            processed_netcdf_filename[test] = standard_postproc.main(exp, \
                                        spinup, \
                                        p_raw_files       = p_raw_files, \
                                        raw_f_subfold     = raw_f_subfold,\
                                        f_vars_to_extract = f_vars_to_extract,\
                                        test = test)
        else:
            log.info('Data already processed for test {}'.format(test))
            processed_netcdf_filename[test] = utils.clean_path(p_wrkdir, 'standard_postproc_{}_{}.nc'.format(test,exp))

    log.banner('End standard-postprocessing')

    log.banner('Start conversion from NetCDF to dataframe')

    if 'welchstest' in tests:
        test = 'welchstest'
        if (actions['test_postproc'][test]):
            # transforming netcdf timeseries into csv file
            df_timeser = timeser_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_output     = p_output,
                lo_export_csvfile = lo_export_csvfile)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_timeser_csv = os.path.join(p_output, 'test_postproc_{}_{}.csv'.format(test,exp))
            df_timeser = pd.read_csv(f_timeser_csv, sep=';')
    else:
        log.warning("Skip Welch's-Test")
        df_timeser = None

    if 'emissions' in tests:
        test = 'emissions'
        if (actions['test_postproc'][test]):
            df_emis = emis_proc_nc_to_df(exp, \
                filename     = processed_netcdf_filename[test],\
                p_output     = p_output, \
                lo_export_csvfile = lo_export_csvfile)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_emis_csv = os.path.join(p_output, 'test_postproc_{}_{}.csv'.format(test,exp))
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
                p_output     = p_output, \
                reference = reference, \
                lo_export_csvfile = lo_export_csvfile)
        else:
            log.info('Processing for test {} already done'.format(test))
            f_pattern_csv = os.path.join(p_output, 'test_postproc_{}_{}.csv'.format(test,exp))
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
                            help = 'exp to proceed')
    parser.add_argument('--p_raw_files', dest = 'p_raw_files',\
                            default = paths.p_raw_files,\
                            help = 'path to raw files')
    parser.add_argument('--p_output', dest='p_output', \
                            default=paths.p_ref_csv_files, \
                            help='path to write csv file')
    parser.add_argument('--raw_f_subfold', dest= 'raw_f_subfold',\
                            default='',\
                            help='Subfolder where the raw data are ')
    parser.add_argument('--f_vars_to_extract',dest='f_vars_to_extract',\
                           default='vars_echam-hammoz.csv',\
                           help = 'File containing variables to anaylse')
    parser.add_argument('--lo_export_csvfile', dest = 'lo_export_csvfile',\
                            default =  True,\
                            help = 'Should a csv file be created')

    parser.add_argument('--lverbose', dest='lverbose', action='store_true')

    args = parser.parse_args()

    main(exp=args.exp,\
         p_raw_files=args.p_raw_files,\
         raw_f_subfold=args.raw_f_subfold,\
         p_output=args.p_output,\
         f_vars_to_extract=args.f_vars_to_extract,\
         lo_export_csvfile=args.lo_export_csvfile,\
         lverbose=args.lverbose)
