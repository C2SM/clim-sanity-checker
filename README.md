# Sanity Checker for climate model 

This tool allows to statistically check the output of a new climate simulation against a set of reference simulations, 
in order to identify systematic bias in the climatological results (due for example to a bug, or too aggressive compiler options). 

This tool is based on a excel tool David Neubaurer (ETHZ) developed for ECHAM-HAMMOZ : 
https://redmine.hammoz.ethz.ch/projects/hammoz/wiki/Reference_experiments_to_test_computing_platform 

It allows to analyze annual global means of a 10 year period (any other period of time is possible as well) for ECHAM-HAMMOZ and ICON.
In general data from other models can be processed as well.

Currently there are 3 different tests available:
   * Welch's t-Test
   * Pattern Correlation Test
   * Emissions Test (I/O)
   
   For more details about the implementation of each test see [test descriptions](test.md).
  
## Structure

This tool consists of three modules that can be run independently and a wrapper to execute them one after each other:

   * [sanity_test.py](sanity_test.py), wrapper that chains modules below
   * [process_data.py](process_data.py), convert raw model output into pd.dataframe
   * [perform_test.py](perform_test.py), apply test based on the pd.dataframe and references stored in [references](ref)
   * [add_exp_to_ref.py](add_exp_to_ref.py), add .csv with results of tests to [references](ref)
  
Each module writes intermediate files to a directory passed with argument --p_stages, the subsequent module then looks into
that directory for files needed. The tool is written in a way, that no time-consuming processing step is done twice.

## Quick start

To use this tool for analysing the experiment called *my_exp*, please follow the following steps:

1. Prepare the python environment

* On Piz Daint (CSCS)
You need to construct your personal python virtual environment based on cray-python PyExtensions modules, containing xarray and begins. 

 > module load cray-python/3.6.5.7 python_virtualenv/15.0.3
 
 > python -m venv --system-site-packages [name_you_choose_for_your_virtualenv]
 
 > source [name_you_choose_for_your_virtualenv]/bin/activate
 
 > pip install --upgrade pip numpy 

 > pip install pandas xarray netcdf4 begins matplotlib

 The next time you log in on Piz Daint, you can get your environment back by typing:
 > source [name_you_choose_for_your_virtualenv]/bin/activate
 
 More infos concerning python virtual environments at CSCS here : https://user.cscs.ch/tools/interactive/python/
 
 2. Get a cdo executable 
 
- On Piz Daint:
 
 > module load CDO

 3. Clone the sanity checker

> git clone git@github.com:C2SM-ICON/clim-sanity-checker.git [folder_name_you_choose_for_clim_sanity_checker]

> cd [folder_name_you_choose_for_clim_sanity_checker]

 4. Create file containing the paths to use (paths.py). 
You need to specify the absolute path to your experiments with the argument -pr .
It is assumed that the experiment you want to analyse is located in [path_to_raw_files]/[my_exp]/[raw_f_subfold].
You will have the possibility to define the variable *raw_f_subfold* in the sanity_test.py arguments (default ='').

For example, to analyse new experiments located in path_to_raw_files against echam-hammoz reference files:

> python paths_init.py -pr [path_to_raw_files]

 5. Analyse your experiment my_exp located in [path_to_raw_files]/[my_exp]/[raw_f_subfold]:
Below the command line to analyse my_exp against the reference files located in 
p_ref_csv_files (default p_ref_csv_files is defined in paths.py, it can be set also in the arguments).

> python sanity_test.py --new-exp [my_exp] 

This will 

- take the raw output of the simulation of my_exp in [p_raw_files]/[my_exp], 

- create a netcdf file containing the timeseries of the annual global means of the 
variables defined in the file variables_to_process (default is variables_to_process/vars_echam-hammoz.csv):
[p_time_serie]/timeser_[my_exp].nc

- create a csv file containing the annual global means:
[p_out_new_exp]/glob_means_[my_exp].csv

- run the Welch's test against the reference experiments located in p_ref_csv_files 
(default defined in in paths.py, it can be set also in the arguments)

- plot the mean and standard deviation of each reference and of the new 
experiment in figure results_new_exp/plot_variables.

- ask the user if he/she wants to add [my_exp] to the pool of reference files. 

Most of the paths used in sanity_test.py are read by default from the file paths.py, 
but the defaults paths can be overriden by passing them in arguments.
For more infos about the argument list, please type python sanity_test.py -h

## Variables to analyse
The definition of the variables to analyse is done in the files located in the folder variables_to_process.
I took the variables David Neubauer usually monitor with ECHAM-HAMMOZ.
A definition of most of these variables can be found in 
Neubauer et al.: The global aerosol–climate model ECHAM6.3–HAM2.3 – Part 2: Cloud evaluation, aerosol radiative forcing, and climate sensitivity, Geosci. Model Dev., 12, 3609–3639, https://doi.org/10.5194/gmd-12-3609-2019, 2019.

The definition of the variables is quite flexible, 
you can define your own variables to analyse either in exanding teh existing file, 
or in creating your own file.
 
## Organisation of sanity_test.py
As already said above, the following steps are conducted in sanity_test.py :
 1. process_data.py : 

 raw files model output [p_raw_files]/[my_exp]/[raw_f_subfold]/* --> [p_time_serie]/timeser_[my_exp].nc --> [p_out_new_exp]/glob_means_[my_exp].csv 
 
 2. read/put all csv files (reference pool & my_exp) into dataframes.

df_new_exp -> dataframe containing my_exp annual global means

df_ref -> dataframe containing all reference annual global means

 3. perform Welch test on the dataframes (df_new_exp against df_ref)

 4. plot averages & std dev of the annual global means

 5. if wanted, add the global annual csv file to the reference files pool, and add the corresponding line in teh Exps_decription file.

## Description of functions

#### paths_init.py
Create the file paths.py containing all the default paths. The following paths are defined:
- p_raw_files     :  Path to the raw files of the experiments (mandatory)
- p_gen           :  General path (default : ./)
- p_scripts       :  Path to the scripts (default : ./)
- p_ref_csv_files :  Path to the pool of csv files containing annual global means per variable, one file per reference experiment (default: ./ref/echam-hammoz)
- p_out_new_exp   :  Path to the folder for the result of new experiment to analyse (default : ./results_new_exp)
- p_wrkdir        :  Path to the working directory (default : ./wrkdir)
- p_time_serie    :  Path to netcdf files of annual global time series (default : ./wrkdir)
- p_f_vars_proc   :  Path to file containnig variables to process and their formula (default : ./variables_to_process)
   
Most of the paths can be changed afterwards using options.

#### sanity_test.py
This is the main script of the tool.
Perform the sanity test, i.e. compare the annual global averages of the new experiment
with the pool of annual global means of the reference files located in [p_ref_csv_files] 
for the variables defined in file f_vars_to_extract. 

The comparison is done using the Welch's Test (https://en.wikipedia.org/wiki/Welch%27s_t-test) . 
The python's method used for the Welch's Test is ttest_ind from scipy.stats 
(https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)  
The result is a csv file containing the p-values and t-values for each variable, 
sorted in ascending p-value. This file is written in p_out_new_exp.

At the end of sanity_test.py, plot_mean_std.py is called, 
and a pdf file containing averages and standard deviations for each variable and experiment is created as well.
          
Sanity_test.py do the whole chain from raw output model to writting out the p-values of the Wesch's test.
If no csv file containig the annual global averages of the new exp [my_exp] is found, process_data.py is called to 
create the latter csv file from all files contained in [p_raw_files]/[my_exp]/[raw_f_subfold] minus spinup (default = 3 files).

#### add_exp_to_ref.py
Ask the user if the global annual csv file should be added to the reference pool of annual global mean csv files.
If yes:
- the csv file is moved from p_out_new_exp into p_ref_csv_files,
- a line is added in the Exp_description.csv file. The content of this line is given by the user.  

#### plot_mean_std.py
Create the pdf file results_new_exp/mean_stdvar_vars_[my_exp].pdf containing, for each variable, a figure of 
mean and std_dev of the annual global means of each experiment.

The horizontal line is the average of all annual global means from all the reference experiments 
and the shaded rectangle the standard deviation of all annual global means from all the reference experiments.

The figures are order by increasing p-value.

#### prepare_csvfiles_ref_echam.py
Script used to create at once all the csv reference files for echam-hammoz.
This script is part of the distribution for documenational purpose. 
It is not used in a standard analyse.

#### process_data.py
Process the raw model output of one experiment into one csv file containing the 
annual global means of the variables defined in file f_vars_to_extract.  

process_data.py first calls std_avrg_using_cdo (independent routine) and second ts_nc_to_df (located in process_data.py).
 1. std_avrg_using_cdo : raw model output -> netcdf time series of global means. 
 2. ts_nc_to_df : netcdf time series of global means -> csv file containing annual global means.

#### std_avrg_using_cdo.py
Computes yearly global means times series of the variables defined in file 
f_vars_to_extract from the raw netcdf model output files using CDO library.
The yearly global means times serie are put in the file timeser_[experiment_name].nc 
located in the directory p_time_serie (per default path p_time_serie written in paths.py).

For the raw model output, all the files located in [p_raw_files]/[my_exp]/[raw_f_subfold] 
minus the spinup (default = 3 files) are used.

The file f_vars_to_extract (located per default in the folder defined in variable p_f_vars_proc in paths.py]) 
contains the definitions of the variables which are computed. 
The expected file is an array with 3 columns separated by ',':
- 1st column : variable name in the output files
- 2nd column : formula to compute this variable, based on native model variable name
- 3rd column : raw output stream name where the native model variable names of the 2nd column can be found. 

The function std_avrg_using_cdo has been based on the script general_proc.sh written by 
Sylvaine Ferrachat (IAC, ETHZ) and tried to be generalized. 

The function has been written in a separate file because it is intended to either be used 
independently of the sanity test tool to replace general_proc.sh, or be replaced by a newer general_proc.sh file by Sylvaine. 

## Missing
1. analyse of variables only over ocean
