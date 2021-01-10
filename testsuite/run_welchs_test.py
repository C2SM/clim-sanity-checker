import os
import subprocess
import  pandas as pd
import xarray as xr
import numpy as np

def test_emission_embed():
    files_generated = generate_data()
    cmd = 'python paths_init.py -pr testsuite/data'
    status, _ =shell_cmd(cmd,py_routine=__name__)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python sanity_test.py -v -e welchs_test -t welchstest --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_welchs_test.csv -c -ts'

    status, _ =shell_cmd(cmd,py_routine=__name__)

    assert status == 0, 'sanity_test.py failed'

    delete_data(files_generated)

def test_emission_chained():
    files_generated = generate_data()
    cmd = 'python paths_init.py -pr testsuite/data'
    status, _ =shell_cmd(cmd,py_routine=__name__)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python process_data.py -v -e welchs_test -t welchstest --f_vars_to_extract vars_welchs_test.csv -c'

    status, _ =shell_cmd(cmd,py_routine=__name__)

    assert status == 0, 'process_data.py failed'

    cmd = 'python perform_test.py -v -e welchs_test -t welchstest  --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_emi_test.csv -c'

    status, _ =shell_cmd(cmd,py_routine=__name__)

    assert status == 0, 'perform_test.py failed'

    delete_data(files_generated)

def generate_data():
    files_generated = []
    data_location = 'testsuite/data/welchs_test'
    os.makedirs(data_location,exist_ok=True)
    time = pd.date_range('2000-01-01', freq="D", periods=366)
    lat = np.arange(10,20,0.1)
    lon = np.arange(10,20,0.1)

    test = xr.DataArray(np.random.rand(366,100,100), coords=[time,lat, lon], dims=['time','lat','lon'],name='T2M')
    months = range(12)
    for m in months:
        test.sel(time=test['time.month'] == m)
        test.to_netcdf(f'{data_location}/{m}_2d_S.nc')
        files_generated.append(f'{data_location}/{m}_2d_S.nc')

    test = xr.DataArray(np.random.rand(366,100,100), coords=[time,lat, lon], dims=['time','lat','lon'],name='TSURF')
    months = range(12)
    for m in months:
        test.sel(time=test['time.month'] == m)
        test.to_netcdf(f'{data_location}/{m}_2d_C.nc')
        files_generated.append(f'{data_location}/{m}_2d_C.nc')

    return files_generated

def delete_data():
    os.remove('testsuite/data/welchs_test/*')

def shell_cmd(cmd,py_routine,lowarn=False):

    """ 
    Send shell command through subprocess.Popen and returns a string 
    containing the cmd output

    lowarn = True -> only a warning is written, no exit (To use with caution!)
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

