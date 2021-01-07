# Description of tests available in clim-sanity-checker
Below you find a brief description about each test available in
this tool.

## Welch's t-Test
This test compares the annual mean values against a set of references. It is able to detect, whether
two samples have equal means.
The function used to do the statistical test is:  
** scipy.stats.ttest_ind **
If a p-value is below 5 %, the test is not passed.

### Additional processing for Welch's t-Test
After the standard preprocessing another processing step using CDO takes place:  
 **cdo  yearmean -fldmean -vertsum**
 
 This command averages the fields vertically (in case 3-D fields are present), reduces 2-D fields to one values and computes the mean values per year.

## Pattern Correlation Test
This test compares the spatial correlation of fields. 
