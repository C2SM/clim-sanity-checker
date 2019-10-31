#
# import modules
import os
import numpy as np
import pandas as pd
import xarray as xr

def nc_to_df(exp = None, \
        p_time_serie = '/project/s903/nedavid/plattform_comparison/', \
        p_output = '/project/s903/colombsi/plattform_comparison/timeseries_csv/', \
        lo_export_csvfile = False):

    '''
Read netcdf file containing global mean values per time and transforms into dataframe.


Arguments: 
exp               = experiment name
p_time_serie      = location of the global means file
p_output          = Definition folder where to write output files (only used if lo_export_csvfile = True)
lo_export_csvfile = if True, export the data into a csv file

C. Siegenthaler, C2SM(ETHZ) , 2019-10
 
    '''
    # Read in file
    filename = os.path.join(p_time_serie, exp,'Data','timeser_{}_2003-2012.nc'.format(exp))
    if not os.path.isfile(filename): 
        print('File {} does not exists'.format(filename))
        return None
    if not os.access(filename,os.R_OK):
        print('No reading permissions for file {}'.format(filename))
        return None
    data = xr.open_dataset(filename)

    # Delete variables
    # useless variable time_bnds
    data = data.drop('time_bnds')
    # 3D vars
    data.drop(labels = ['AOD', 'W_LARGE', 'W_TURB', 'u', 'v', 'omega', 'incl_cdnc', 'incl_icnc'])

    # removed degenerated dimensions
    data = data.squeeze(drop = True)

    # transforms into dataframe
    df_data = data.to_dataframe()

    # export in a file
    if lo_export_csvfile:
        os.makedirs(p_output, exist_ok=True)
        export_csv = df_data.to_csv(os.path.join(p_output,'glob_means_{}.csv'.format(exp)), index = None, header=True, sep = ';')

    return(df_data)

