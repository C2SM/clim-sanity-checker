import subprocess
import os
import pandas as pd
import xarray as xr
import numpy as np
import netCDF4 as nc


def shell_cmd(cmd,lowarn=False):

    """ 
    Send shell command through subprocess.Popen and returns a string 
    containing the cmd output
    """

    # send cmd to be executed
    p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         universal_newlines=True)

    # gets the output of the cmd
    out, err = p.communicate()
    print(str(out))
    print(str(err))

    return p.returncode,(str(out) + str(err))

def generate_data(input_dir,folder,identifier,field):

    files_generated = []
    data_location = os.path.join(input_dir,folder)
    os.makedirs(data_location,exist_ok=True)

    for year in range(2000,2006):
        time = pd.date_range('{}-01-01'.format(year),
                             freq="D", 
                             periods=365)
        lat = np.arange(10,20,0.1)
        lon = np.arange(10,20,0.1)

        test = xr.DataArray(np.random.rand(365,100,100),
                            coords=[time,lat, lon],
                            dims=['time','lat','lon'],
                            name=field)
        months = range(1,13)
        for m in months:
            month = '{:0>2d}'.format(m)
            filename = '{}/{}_{}_{}.nc'.format(data_location,
                                               year,
                                               month,
                                               identifier)
            one_month = test.sel(time=test['time.month'] == m)
            one_month.to_netcdf(filename)
            files_generated.append(filename)

    return files_generated

def generate_identical_data(input_dir,folder,identifier,field):

    files_generated = []
    data_location = os.path.join(input_dir,folder)
    os.makedirs(data_location,exist_ok=True)

    for year in range(2000,2006):
        time = pd.date_range('{}-01-01'.format(year), freq="d", periods=365)
        lat = np.arange(10,20,0.1)
        lon = np.arange(10,20,0.1)

        test = xr.dataarray(np.full((365,100,100),0.45), 
                            coords=[time,lat, lon], 
                            dims=['time','lat','lon'],
                            name=field)
        months = range(1,13)
        for m in months:
            month = '{:0>2d}'.format(m)
            filename = '{}/{}_{}_{}.nc'.format(data_location,
                                               year,month,
                                               identifier)
            one_month = test.sel(time=test['time.month'] == m)
            one_month.to_netcdf(filename)
            files_generated.append(filename)

    return files_generated

def generate_ref(ref_dir,name,fields):

    os.makedirs(ref_dir,exist_ok=True)

    files_generated = []
    time = pd.date_range('2002-12-31 12:00:00', freq="D", periods=1)
    lat = np.arange(10,20,0.1)
    lon = np.arange(10,20,0.1)

    test = xr.DataArray()
    ds_to_merge = []
    for field in fields:
        data = np.full((1,100,100),0.45)
        test = xr.DataArray(data, 
                            coords=[time,lat, lon], 
                            dims=['time','lat','lon'],
                            name=field)
        ds_to_merge.append(test)

    merged_ds = xr.merge(ds_to_merge)
    filename_raw = '{}/{}_raw'.format(ref_dir,name) 
    merged_ds.to_netcdf(filename_raw)
    files_generated.append(filename_raw)

    filename = '{}/{}'.format(ref_dir,name) 
    cmd = 'cdo -setctomiss,-9e+33 {} {}'.format(filename_raw,filename)
    status, _ = shell_cmd(cmd)
    assert status == 0
    files_generated.append(filename)

    return files_generated

def generate_test(input_dir,folder,identifier,field):

    files_generated = []
    data_location = os.path.join(input_dir,folder)
    os.makedirs(data_location,exist_ok=True)

    data = np.full((1,100,100),0.45)

    for year in range(2000,2006):
        lat = np.arange(10,20,0.1)
        lon = np.arange(10,20,0.1)

        months = range(1,13)
        for m in months:

            month = '{:0>2d}'.format(m)
            filename = '{}/{}_{}_{}.nc'.format(data_location,
                                               year,
                                               month,
                                               identifier)
            timestring = '{}{}01'.format(year,month)
            time = np.float32(int(timestring))

            netcdf = nc.Dataset(filename, "w", format='NETCDF4')
            netcdf.createDimension('lon',100)
            netcdf.createDimension('lat',100)
            netcdf.createDimension('time', None)

            time_var = netcdf.createVariable('time', np.float32, ('time',))
            time_var.calendar = 'proleptic_gregorian'
            time_var[0] = timestring
            nc.date2num(time,calendar='proleptic_gregorian')
            field_var = netcdf.createVariable(field,
                                              np.float32,('time',
                                                          'lat',
                                                          'lon'))

            field_var[0,:,:] = data
            netcdf.close()

            files_generated.append(filename)

    return files_generated


def delete_data(files_to_delete):
    for file in files_to_delete:
        os.remove(file)
