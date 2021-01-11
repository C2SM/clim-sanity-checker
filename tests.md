# Description of tests available in clim-sanity-checker
Below you find a brief description about each test available in
this tool.

## Welch's t-Test
This test compares the annual mean values against a set of references. It is able to detect, whether
two samples have equal means.
The function used to do the statistical test is:  
**scipy.stats.ttest_ind**  
If a p-value is below 5 %, the test is not passed.

#### Additional processing for Welch's t-Test
After the standard preprocessing another processing step using CDO takes place:  
 **cdo  yearmean -fldmean -vertsum**
 
 This command sums the fields vertically (in case 3-D fields are present), reduces 2-D fields to one value and computes the mean values per year.

## Pattern Correlation Test
This test compares the spatial correlation of fields. To do so
the CDO operator *-fldcor* is applied. To have more sensitiv results
the values are squared with the operator *-sqr*.

If the R^2 values is below 0.98 the test is not passed.

In order to apply this test, a reference netCDF is needed. Per default a reference is downloaded from the ftp-server of ETHZ.
The link needs to be defined in a file, having the same name ans location as the desired f_vars_to_proc.
As an example [vars_echam-hammoz.csv](variables_to_process/pattern_correlation/vars_echam-hammoz.csv) and [ftp_echam-hammoz.txt](variables_to_process/pattern_correlation/ftp_echam-hammoz.txt) is a matching pair.

In case one wants to use a custom reference file, the file can be passed with the *-f_pattern_ref* argument.

#### Additional processing for Pattern Correlation Test
After the standars preprocessing another processing step using CDO takes place:  
**cdo timmean -yearmean -vertsum**  

This command sums the fields vertically (in case 3-D fields are present), computes the mean values of each gridcell per year,  
and finally averages these values over the entire period (usually 10 years).

## Emission Test
This test checks if the emissions fed into the model as input is correctly processed during the model run. It computes
the relative deviation of the averages emissions over the entire simulated period.
In general a relative deviation of up to 1 % is still ok due to runding errors of floating point operations.

#### Additional processing for Emission Test
After the standard preprocessing another processing step using CDO takes place:  
**cdo timmean -fldmean -vertsum**  

This command sums the fields vertically (in case 3-D fields are present), reduces 2-D fields to one value and computes the average over the entire period.
