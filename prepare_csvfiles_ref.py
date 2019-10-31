# Script to prepare reference netcdf files into csv files
# C.Siegenthaler, 2019-10


from process_data import nc_to_df
import begin
import os
import pandas as pd

@begin.start


def run(p_time_serie      = '/project/s903/nedavid/plattform_comparison/', \
        p_output_csv_file = '/project/s903/colombsi/plattform_comparison/timeseries_csv/', \
        lo_export_csvfile = True)

    # get experiments to consider
    exps = os.listdir(p_time_serie)

    # testing procedure -> euler_centos74_i17 is considered to be new exp
    exps.remove('euler_REF_10y_i18')
    
    # delete emi_inpout folder
    exps.remove('emi_input')

    # initialize dataframe
    df = None

    # loop over exps
    for iexp, exp in enumerate(exps):

       # print info
       print('Processing file: {}'.format(exp))
        
       # test if file exist:
       if not os.path.isdir(p_time_serie):
            print('Warning : Folder does not exist: {}'.format(p_time_serie))

       # read data for exp
       df = nc_to_df(exp, \
                     p_time_serie = p_time_serie, \
                     p_output = p_output_csv_file, \
                     lo_export_csvfile = lo_export_csvfile)


