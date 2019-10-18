#
# import modules
import os
import numpy as np
import pandas as pd
import xarray as xr
import begin

@begin.start

def run(exp = None, \
        p_time_serie = '/project/s903/nedavid/plattform_comparison/', \
        p_output = '/project/s903/colombsi/plattform_comparison_data/timeseries/', \
        lo_export_csvfile = False):

    '''
Read netcdf file containing global mean values per time and transforms into dataframe

Arguments: 
exp          = experiment name
p_time_serie = location of the global means file
p_output     = "Definition folder where to write output files"
 
    '''

    # prepare working directory
    os.makedirs(p_output, exist_ok=True)

    # Read in file
    filename = os.path.join(p_time_serie, exp,'Data','timeser_{}_2003-2012.nc'.format(exp))
    data = xr.open_dataset(filename)

    # removed degenarated dimensions
    data = data.squeeze(drop = True)

    # delete 3D vars
    data.drop(labels = ['AOD', 'W_LARGE', 'W_TURB', 'u', 'v', 'omega', 'incl_cdnc', 'incl_icnc'])

    # transforms into dataframe
    df_data = data.to_dataframe()

    # export in a file
    if lo_export_csvfile:
        export_csv = df_data.to_csv(os.path.join(p_output,'glob_means_{}.csv'.format(exp)), index = None, header=True, sep = ';')

    return(df_data)
