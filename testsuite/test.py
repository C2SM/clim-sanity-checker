import  pandas as pd
import xarray as xr
import utils 
import numpy as np


time = pd.date_range("2000-01-01", freq="D", periods=366)
lat = np.arange(10,20,0.1)
lon = np.arange(10,20,0.1)

test = xr.DataArray(np.random.rand(366,100,100), coords=[time,lat, lon], dims=['time','lat','lon'],name='test1')
print(test)
months = range(12)
for m in months:
    test.sel(time=test['time.month'] == m)
    test.to_netcdf(f'{m}.nc')

