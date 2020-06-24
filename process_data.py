#
import begin
import os
import pandas as pd
import xarray as xr
from config_path import paths_cscs as paths
import std_avrg_using_cdo
import argparse

def ts_nc_to_df(exp, \
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
    
    # list of variables in the timeserie netcdf file to drop (not to put into the dataframe)
    vars_to_drop = []

    # print warnings
    if not os.path.isfile(filename): 
        print('File {} does not exists'.format(filename))
        return None
    if not os.access(filename,os.R_OK):
        print('No reading permissions for file {}'.format(filename))
        return None
    # print info
    print('Processing file: {}'.format(filename))


    # open dataset
    data = xr.open_dataset(filename)

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

    print('Finished ts_nc_to_df for file {}'.format(filename))

    # export in a file
    if lo_export_csvfile:
        os.makedirs(p_output, exist_ok=True)
        csv_filename = os.path.join(p_output,'glob_means_{}.csv'.format(exp))
        df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
        print('CSV file can be found here: {}'.format(csv_filename))     
    

    return(df_data)


def main(exp,\
       p_raw_files  = paths.p_raw_files,\
       p_output     = paths.p_ref_csv_files,\
       lo_export_csvfile = False,\
       lverbose = False):
    '''
Process exp 
    '''

# transform Raw output into netcdf timeserie using cdo commands
    timeser_filename = std_avrg_using_cdo.main(exp,\
                             p_raw_files       = p_raw_files,\
                             p_time_serie      = paths.wrk_dir,\
                             wrk_dir           = paths.wrk_dir,\
                             spinup            = 3,\
                             f_vars_to_extract = os.path.join(paths.p_gen,'./variables_to_process_echam.csv'),\
                             lverbose          = lverbose)

# transforming netcdf timeseries into csv file
    ts_nc_to_df(exp, \
        filename     = timeser_filename,\
        p_output     = p_output,
        lo_export_csvfile = lo_export_csvfile)
    return()


if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--exp','-e', dest = 'exp',\
                            help = 'exp to proceed')

    parser.add_argument('--p_raw_files', dest = 'p_raw_files',\
                            default = paths.p_raw_files,\
                            help = 'path to raw files')

    parser.add_argument('--p_output', dest = 'p_output',\
                            default = paths.p_ref_csv_files,\
                            help = 'path to write csv file')

    parser.add_argument('--lo_export_csvfile', dest = 'lo_export_csvfile',\
                            default =  False,\
                            help = 'Should a csv file be created')

    parser.add_argument('--lverbose', dest='lverbose', action='store_true')

    args = parser.parse_args()

    main(args.exp, args.p_raw_files, args.p_output, args.lo_export_csvfile, args.lverbose)
