# Script to test sanity of a n HAMMOZ run
# C.Siegenthaler, 2019


from shell_interactions import sys_cmd
from process_data import nc_to_df
import begin
import os
import pandas as pd

def cdo_process(filename) :
    return()

class table_ref:
    def __init__(self, file_summary):
        # tabs in the excel file
        tabs_table = {'exp' : 'Experiment description', \
                      'globmean' : 'Global annual mean', \
                      'patcor' : 'Pattern correlation', \
                      'emi' : 'Emissions'}
        # assigne one key per tab
        for sh_name, tab in tabs_table.items():
            self.__dict__[sh_name] = pd.read_excel(file_summary, tab)

        # keep track of the tab names
        self.tabs = tabs_table

@begin.start

def run(p_time_serie='/project/s903/nedavid/plattform_comparison/', \
        file_sum = '/project/s903/colombsi/plattform_comparison/Platform_comparison.xlsx',\
        wrk_dir = '/project/s903/colombsi/plattform_comparison') :

     # new experiment to test
     # -------------------------------------------------------------
     # name and path of experiment to test
     new_exp = 'euler_REF_10y_i18'
     p_new_exp = '/project/s903/nedavid/plattform_comparison/'

     # create dataframe out of netcdf timeserie
     df_new_exp = nc_to_df(new_exp, \
                           p_time_serie = p_new_exp, \
             #        p_output = '/project/s903/colombsi/plattform_comparison/timeseries_csv/', \
                           lo_export_csvfile=True)


     # data of reference pool
     # ---------------------------------------------------------------
     # get experiments of reference folder
     p_csv_ref = '/project/s903/colombsi/plattform_comparison/timeseries_csv'

     # get experiments to consider
     exps = os.listdir(p_csv_ref)

     # create big dataframe 
     #for fexp in exps:

      #   # full path to csv file
      #   f_fp_exp = os.path.join(p_csv_ref,fexp)

         # read the csv file
       #  df_exp = pd.read_csv(f_fp_exp)

        # # put all data in one big dataframe
        # if (df_exp is not None):
        #    print('Hello 0')
        #    df[experiment] = exp

         #   print(df)
#
#            if (df_tot is None):
#                df_tot = df
#                print('Hello 1')
#            else:
#                print('Heloo 2')
#                print(df_tot)
#                print(df_tot.merge(df))
#             #   exit()

#       print('----------------------------------')

        

#    print('HEllo end')
#
#    expname=exp
#    # prepare working directory
#    os.makedirs(wrk_dir,exist_ok=True)
#    os.chdir(wrk_dir)
#
#    # data of reference experiments
#    data_ref_file = table_ref(file_summary)
#
#    # global mean new experiment
#    p_globmean_newexp = os.path.join(oldexps_path, expname , 'Data/analysis_{}_2003-2012.txt'.format(expname))
 #   data_newexp_glob = pd.read_csv(p_globmean_newexp, sep='\s+', header=1)

    # standard deviation new experiment
#    tmp_timeser_newexp = p_globmean_newexp.replace('analysis', 'timeser').rstrip('.txt')
#    p_timeser_newexp = os.path.join(wrk_dir, (os.path.basename(tmp_timeser_newexp) + '.txt'))
    # compute std deviation
#    sys_cmd('cdo infov -timstd {}.nc > {}'.format(tmp_timeser_newexp, p_timeser_newexp))
#    data_newexp_std = pd.read_csv(p_timeser_newexp, sep=' : ', usecols=[2,3], skiprows = [0], names = ['std','name'])

#    data_newexp_std = data_newexp_std.reindex(columns=['name','std'])
#    print(data_newexp_std)
#    print(data_newexp_glob)



