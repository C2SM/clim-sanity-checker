# Module arguments
To all modules a variety of command-line arguments can be passed to specify the type of tests, the location of the raw data or to increase verbosity.
Below you find a detailed description of each argument available.
Another way to get the arguments for each module is to run:  
*python your_module.py --help*

|argument|description   |for modules |default| 
|---|---|---|---|
|--exp, -e        |name of your experiment, should be unique|all | None |
|--p_raw_files  |absolute or relative path to your raw files, this path is extended with the argument *--exp* and *--raw_f_subfold* the following: [p_raw_files / exp / raw_f_subfold]  | sanitiy_test.py, process_data.py  | defined in paths.py  |
|--raw_f_subfold| Subfolder where the raw data is, ECHAM-specific | sanity_test.py, process_data.py | ' '|
|--p_stages  | absolute or relative path to the folder where intermediate processing steps of the modules are stored. **Caution:** Needs free disk space |all  | defined in paths.py  |
|--wrkdir| absolute or relative path to the working directory. **Caution:** Needs free disk space | all | defined in paths.py |
| --tests, -t| test to apply on your data|all| welchstest pattern_correlation emissions|
|--p_ref_csv_files| absolute or relative path to reference files. This path is extended automatically for each test the following [p_ref_csv_files / test] | sanity_test.py, perform_test.py, add_exp_to_ref.py| defined in paths.py|
|--f_vars_to_extract | file name containing variables to analyse. This file needs to be located in [variables_to_process / test] | sanity_test.py, process_data.py, perform_test.py| vars_echam-hammoz.csv|
|--clean, -c| Redo all processing steps from module *process_data.py* | sanity_test.py, process_data.py | not set|
|--verbose, -v | Debug output | all | not set|
|--spinup| Integer, indicates the number of months the model output is not considered due to model spinup| sanity_test.py, process_data.py | 3|
