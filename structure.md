# Module description
All important processing steps for each of the three modules is described below. Only steps relevant to data processing are described.

## process_data.py

#### standard_postproc
Computes the variables defined in file 
f_vars_to_extract from the raw netcdf model output files using CDO library.
For the raw model output, all the files located in [p_raw_files]/[exp]/[raw_f_subfold] 
minus the spinup (default = 3 files) are used.

The file f_vars_to_extract 
contains the definitions of the variables which are computed. 
The expected file is an array with 3 columns separated by ',':
- 1st column : variable name in the output files
- 2nd column : formula to compute this variable, based on native model variable name
- 3rd column : raw output stream name where the native model variable names of the 2nd column can be found. 

Files with a problem are skipped. All variables are then merged into one single netCDF-file that is stored in
the directory passed as argument *--p_stages*

The function in combination with timeser_proc_nc_to_df is been based on the script general_proc.sh written by 
Sylvaine Ferrachat (IAC, ETHZ) and tried to be generalized.

#### timeser_proc_nc_to_df
Process the netCDF produced in **standard_postproc** further using CDO to get a timeseries of annual mean values for each field.
Finally a .csv file of this timeseries is stored (this file serves as a reference if the experiment is added to the reference pool).

#### pattern_proc_nc_to_df
Process the netCDF produced in **standard_postproc** further using CDO to get multi-annual means per gridcell for each field.
Then the actual field-correlation using CDO is computed. The resulting R^2-values for each field is stored in a .csv file for later use.
This .csv file serves as described above as a reference if the experiment is added to the reference pool.

#### emis_proc_nc_to_df
Process the netCDF produced in **standard_postproc** further using CDO to get a mean value over the entire period for each field.
This .csv file serves as described above as a reference if the experiment is added to the reference pool.
