# Script to prepare reference netcdf files into csv files
# C.Siegenthaler, 2019-10


import process_data
import begin
import os
import paths      # the file paths.py is written by paths_init.py

@begin.start


def run(p_raw_files       = paths.p_raw_files, \
        p_output_csv_file = paths.p_ref_csv_files, \
        lo_export_csvfile = True,\
        lverbose          = False):

    # get experiments to consider
    exps = os.listdir(p_raw_files)

    # delete emi_inpout folder
    exps.remove('emi_input')

    # remove 3 exps that should not be in reference pool (communication David Neubauer, 2020-06-24)
    [exps.remove(e) for e in ['euler_REF_10y_i14_branch','euler_REF_10y_i17_branch','sanity_plt_daint_201810']]
 
    # if output dir does not exist, create it
    if not os.path.isdir(p_output_csv_file):
        os.mkdir(p_output_csv_file)    
        print('Create output directory: {}'.format(p_output_csv_file))

    # loop over exps
    for iexp, exp in enumerate(exps):

       # print info
       print('Processing experiment: {}'.format(exp))
      
       # initialize dataframe
       df = None  

       # read data for exp
       df = process_data.main(exp, \
                     p_raw_files = p_raw_files, \
                     p_output = p_output_csv_file, \
                     raw_f_subfold='Raw', \
                     f_vars_to_extract='vars_echam-hammoz.csv',\
                     lo_export_csvfile = lo_export_csvfile,\
                     lverbose = lverbose)
       print('---------------------------------------------------------------------')

    print('prepare_csvfiles_ref.py finished')

