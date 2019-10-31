# Script to prepare reference netcdf files into csv files
# C.Siegenthaler, 2019-10


from process_data import nc_to_df
import begin
import os
import pandas as pd

@begin.start


def run(p_time_serie='/project/s903/nedavid/plattform_comparison/', \
        file_sum = '/project/s903/colombsi/plattform_comparison/Platform_comparison.xlsx',\
        wrk_dir = '/project/s903/colombsi/plattform_comparison') :

    # get experiments to consider
    exps = os.listdir(p_time_serie)

    # testing procedure -> euler_centos74_i17 is considered to be new exp
    exps.remove('euler_REF_10y_i18')
    
    # delete emi_inpout folder
    exps.remove('emi_input')

    # initialize dataframe
    df_tot = None
    df = None

    # loop over exps
    for iexp, exp in enumerate(exps):
        
       # test if file exist:
       if not os.path.isfile(p_time_serie):
            print('Warning : File does not exist: {}'.format(p_time_serie))

       # read data for exp
       #   try:
       df = nc_to_df(exp, \
                     p_time_serie = p_time_serie, \
             #        p_output = '/project/s903/colombsi/plattform_comparison/timeseries_csv/', \
                     lo_export_csvfile=True)


