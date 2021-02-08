## Reference Database
A key component of this tool are the references (experiments that have correct results). By running the same experiment (identical namelists, input-data, emission-scenarios, etc.) but with different compilers or on different machines one can cross-compare and verify these installations. 
It is recommened to use at least a 10-year period as experiment duration, for shorter periods the tests could fail due to rounding error even in case of correct results.
If one configuration, i.e. GCC on Piz Daint, does not give results within the statistical tolerance of each test, there is very likely a bug or a problem.

### Structure
The reference experiments are stored as .csv in the folder ref(add_reff). Any other location, even outside of the clim-sanity-checker repository is possible.  
Just pass the folder with *--p_ref_csv_files*. The structure of the reference folder needs to be as follows:

*[p_ref_csv_files / current_test/ref_a.csv]*  

This folder must also contain an additional .csv file providing a table with all essential information about the experiments.
See [Exps_description.csv](ref/echam-hammoz/Exps_description.csv) as an example.

The .csv files itself store either the global [mean-values](ref/echam-hammoz/welch/glob_means_daint_REF_10y.csv) (used for Welch's t-test) or the results of the test in the 
respective test-metric like [R^2](ref/echam-hammoz/fldcor/fldcor_daint_REF_10y.csv) (all other tests).

### Adding experiments to the database
There are two possible options to add experiments with the module
*[add_exp_to_ref.py](add_exp_to_ref.py)*:

* Run sanity_test.py and type *yes* when asked by the clim-sanity-checker  
or  
* manually run add_exp_to_ref.py with the correct command-line arguments  

The clim-sanity-checker prints out the correct command-line arguments in case on types *no*:  

`If you want to add the experiment daint_REF_10y to the reference pool later on, type the following line when you are ready:`

`python add_exp_to_ref.py --exp daint_REF_10y --tests emi --p_stages stages --p_ref_csv_files ref/echam-hammoz`

You are then asked to enter some details about the experiment:  

**Basic information**  

* Experiment name
* Platform;OS
* Date of experiment (month yyyy)

**Compiler Options**  

* Compiler (with version)
* Optimisation level (-OX)
-fast-transcendentals (y/n)
* -no-prec-sqrt (y/n)
* -no-prec-div (y/n)

**Test performed for this experiment**  

* welch (y/n)
* fldcor (y/n)
* rmse (y/n)
* emi (y/n)

Finally a commit message needs to be defined. The clim-sanity-checker creates a new branch and commits all new files of this experiments
into the reference database.

**The final push to the remote needs to be done manually by the user!**


### Experiment Settings
Currently there is one setting available for ECHAM-HAMMOZ and ICON.


#### ICON
The setting for the references in [icon](ref/icon) is [atm_amip](https://github.com/C2SM-ICON/icon/blob/master/run/exp.atm_amip). This is the standard
configuration of ICON for climate-simulations. From the experiment description in the header of the runscript:  

*This file describes an AMIP experiment based on the non-hydrostatic atmosphere and the
 ECHAM physics. The experiment is intialized from IFS analysis files and uses transient
boundary conditions for:  
-SST and sea ice  
-spectral solar irradiation  
-well mixed greenhouse gases CO2, CH4, N2O, CFCs  
-O3 concentration  
-tropospheric aerosol optical properties  
-stratospheric volcanic aerosol optical properties*

#### ECHAM-HAMMOZ
The setting for the references in [echam-hammoz](ref/echam-hammoz) is the following (taken from David Neubauer):  
ECHAM6.3-HAM2.3-MOZ1.0 release tag (https://redmine.hammoz.ethz.ch/projects/hammoz/repository/show/echam6-hammoz/tags/echam6.3.0-ham2.3-moz1.0)  
Default run configuration for HAM-M7  
v0002 Input file distribution (corresponding to setup_templates/run_examples/run_defaults_echam6-ham)  					
(T63L47GR15; ACCMIP_interpolated emissions RCP45 transient emissions; 2003-2012; SST/SIC climatology 1979-2008,...)					
