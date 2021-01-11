import subprocess
import os
import pandas as pd
import xarray as xr
import numpy as np

def shell_cmd(cmd,lowarn=False):

    """ 
    Send shell command through subprocess.Popen and returns a string 
    containing the cmd output
    """

    # send cmd to be executed
    p = subprocess.Popen(cmd, shell=True, \
                         stdout = subprocess.PIPE, stderr = subprocess.PIPE, \
                         universal_newlines=True)

    # gets the output of the cmd
    out, err = p.communicate()
    print(str(out))
    print(str(err))

    return p.returncode,(str(out)+str(err))

def generate_data(input_dir,folder,identifier,field):

    files_generated = []
    data_location = os.path.join(input_dir,folder)
    os.makedirs(data_location,exist_ok=True)

    for year in range(2000,2006):
        time = pd.date_range('{}-01-01'.format(year), freq="D", periods=365)
        lat = np.arange(10,20,0.1)
        lon = np.arange(10,20,0.1)

        test = xr.DataArray(np.random.rand(365,100,100), coords=[time,lat, lon], dims=['time','lat','lon'],name=field)
        months = range(1,13)
        for m in months:
            month = '{:0>2d}'.format(m)
            filename = '{}/{}_{}_{}.nc'.format(data_location,year,month,identifier)
            one_month = test.sel(time=test['time.month'] == m)
            one_month.to_netcdf(filename)
            files_generated.append(filename)

    return files_generated

def delete_data(files_to_delete):
    for file in files_to_delete:
        os.remove(file)
