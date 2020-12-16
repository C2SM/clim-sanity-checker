#
import os
import xarray as xr
import paths                    # the file paths.py is written by paths_init.py
import std_avrg_using_cdo
import pattern_correlation
import argparse
import shell_utilities as su          # file shell_utilities.py part of the distribution

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
        print('ts_nc_to_df : File {} does not exists'.format(filename))
        return None
    if not os.access(filename,os.R_OK):
        print('ts_nc_to_df : No reading permissions for file {}'.format(filename))
        return None
    # print info
    print('ts_nc_to_df : Processing file : {}'.format(filename))


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
        print('ts_nc_to_df : CSV file can be found here: {}'.format(csv_filename))     
    

    return(df_data)

def field_correlation(exp, \
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
    
    # list of variables in the timeserie netcdf file to drop (not to put into the dataframe)
    vars_to_drop = []

    # print warnings
    if not os.path.isfile(filename): 
        print('field_correlation : File {} does not exists'.format(filename))
        return None

    if not os.access(filename,os.R_OK):
        print('field_correlation : No reading permissions for file {}'.format(filename))
        return None

    if not os.access(reference,os.R_OK):
        print('field_correlation : No reading permissions for file {}'.format(reference))
        return None
    # print info
    print('field_correlation : Processing file : {}'.format(filename))

    ofile_str = 'field_corr.nc'
    cdo_cmd = 'cdo fldcor {} {} {}'.format(filename,reference,ofile_str) 
    su.shell_cmd (cdo_cmd,py_routine='pattern_correlation')
    
    
    # open dataset
    data = xr.open_dataset(ofile_str)

    # Delete variables
    # useless variable time_bnds
    if ('time_bnds' in data.keys()):
        data = data.drop('time_bnds')
    # 3D vars
    if len(vars_to_drop)>0:
        data.drop(labels = vars_to_drop)

    # transforms into dataframe
    df_data = data.to_dataframe()

    print('Finished field_correlation for file {}'.format(filename))

    # export in a file
    if lo_export_csvfile:
        os.makedirs(p_output, exist_ok=True)
        csv_filename = os.path.join(p_output,'glob_corr_{}.csv'.format(exp))
        df_data.to_csv(csv_filename, index = None, header=True, sep = ';')
        print('field_correlation : CSV file can be found here: {}'.format(csv_filename))     
    

    return(df_data)


def main(exp,\
       p_raw_files  = paths.p_raw_files,\
       p_output     = paths.p_out_new_exp,\
       raw_f_subfold     = '',\
       f_vars_to_extract = 'vars_echam-hammoz.csv',\
       lo_export_csvfile = True,\
       lverbose = False):
    '''
Process exp 
    '''

# transform Raw output into netcdf timeserie using cdo commands
    timeser_filename = std_avrg_using_cdo.main(exp,\
                             p_raw_files       = p_raw_files, \
                             raw_f_subfold     = raw_f_subfold,\
                             f_vars_to_extract = f_vars_to_extract,\
                             lverbose          = lverbose)

# transforming netcdf timeseries into csv file
    df_data = ts_nc_to_df(exp, \
        filename     = timeser_filename,\
        p_output     = p_output,
        lo_export_csvfile = lo_export_csvfile)

    reference = '/scratch/juckerj/sanity_check/ref_data/yearmean_GCC.nc'

# transform Raw output into netcdf global mean using cdo commands
    global_mean_filename = pattern_correlation.main(exp,\
                             p_raw_files       = p_raw_files, \
                             raw_f_subfold     = raw_f_subfold,\
                             f_vars_to_extract = f_vars_to_extract,\
                             lverbose          = lverbose)

# field correlarion using CDO with a given refercence
    df_corr = field_correlation(exp, \
        filename     = global_mean_filename,\
        p_output     = p_output, \
        reference = reference, \
        lo_export_csvfile = lo_export_csvfile)
     

    return(df_data,df_corr)


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
