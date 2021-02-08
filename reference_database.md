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
In order to add a new experiment to the database please use the
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
