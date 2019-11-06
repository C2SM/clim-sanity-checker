# Script to test sanity of a n HAMMOZ run
# C.Siegenthaler, 2019


from shell_interactions import sys_cmd
from process_data import nc_to_df
import begin
import os
import pandas as pd
import glob
from scipy import stats
import plot_mean_std as plt
from config_path import paths_mac as paths


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

def df_drop_inplace(df,col_list):
    ''' Drop columns in col_list if the column exists '''

    # list of columns to drop (which are present in df
    list_to_drop = [col for col in col_list if col in df.keys()]

    # drop list of existing columns
    df.drop(labels=list_to_drop,axis=1,inplace=True)

    return

def create_big_df(list_csv_files, filename_csv=''):
    '''
    Create big dataframe form list of csv files
    :param list_csv_files: list of csv files for the big dataframe
    :return: big dataframe containing the whole data
    '''

    # initialise big empty dataframe
    df_tot = pd.DataFrame()

    # create big dataframe
    for fexp in list_csv_files:

        exp = os.path.basename(fexp).rstrip('.csv').replace('glob_means_','')

        # read the csv file
        if os.path.isfile(fexp):
            df_exp = pd.read_csv(fexp, sep=';')
            df_exp['exp'] = exp

            # append dataframe of exp to the total dataframe
            df_tot = df_tot.append(df_exp, sort = False)

        else:
            print('Warning csv file is not a file : {}'.format(fexp))

    if len(filename_csv) > 0 :
        df_tot.to_csv(filename_csv, sep = ';')

    return df_tot

def welch_test_all_var(df_a, df_b , filename_student_test = ''):
    '''
    Perform Welch t-test for each variable fo dataframe df_b
    :param df_a: reference datframe, containing big sample
    :param df_b: datframe containing data to test
    :param filename_student_test: filename for writing result of t-test result into a csv file
    :return: result of the student test in a dataframe
    '''

    # initialisation for construction dataframe (much faster to use list than dataframe.append)
    row_list_df = []

    for var in df_b.keys():
        if 'exp' in var:
            continue

        # Welch's t-test
        t, p = stats.ttest_ind(df_a[var], df_b[var], equal_var = False, nan_policy='omit')

        # append results for construction datframe df_result
        dict1 = {'variable' : var, 't-value' : t , 'p-value' : p}
        row_list_df.append(dict1)

    # construction dataframe
    df_result = pd.DataFrame(row_list_df, columns=['variable','t-value','p-value'] )

    # sort per p value
    df_result.sort_values(by=['p-value'], inplace=True)

    # if a filename is given, write the student-stest result into the file named filename_student_test
    if len(filename_student_test) > 0 :
        df_result.to_csv(filename_student_test, sep = ',')

    return (df_result)

def print_warnings_pvalues(df_result, p_treshold, new_exp):
    ''' Print warnings for the variables which have a small p value '''

    label_new_col = 'p-value < {} %'.format(p_treshold * 100.)

    # Chek if p value small
    df_result[label_new_col] = df_result['p-value'] < p_treshold

    # datframe containing only variable with low p (for print the warnings
    df_low_p = df_result[df_result[label_new_col]]

    if (df_low_p.size > 0):
        print('WARNING :: the following variables gives low p-value in the comparison between the references and the new experiment {} :'.format(new_exp))
        print (df_low_p)

    return (df_result)


@begin.start

def run(p_ref_csv_files = paths.p_ref_csv_files,\
        wrk_dir = paths.wrk_dir,
        p_new_exp = paths.p_new_exp):

     # go in workdir
     if len(wrk_dir) > 0 :
         os.chdir((wrk_dir))


     # new experiment to test
     # -------------------------------------------------------------
     # name and path of experiment to test
     new_exp = 'euler_REF_10y_i18'

     # get data new exp in dataframe
     f_new_exp_csv = os.path.join(p_new_exp, 'glob_means_{}.csv'.format(new_exp))
     if os.path.isfile(f_new_exp_csv):
         df_new_exp = pd.read_csv(f_new_exp_csv, sep=';')
     else:
         # create dataframe out of netcdf timeserie
         df_new_exp = nc_to_df(new_exp,\
                               p_time_serie=p_new_exp,\
                               p_output=p_new_exp,\
                               lo_export_csvfile=True)
     df_new_exp['exp'] = new_exp

     # data of reference pool
     # ---------------------------------------------------------------
     # get experiments of reference folder (in the fiuture, download from Git)
     # download files into p_csv_files

     # list of paths to all csv files
     p_csv_files = glob.glob(os.path.join(p_ref_csv_files,'*csv'))

     # create big dataframe containing all reference exps
     df_ref = create_big_df(list_csv_files=p_csv_files)

     # cleaning (in case it ws not done properly in the transition from netcdf files into csv format
     df_drop_inplace(df_ref, col_list = ['AOD', 'W_LARGE', 'W_TURB', 'u', 'v', 'omega', 'incl_cdnc', 'incl_icnc'])
     df_drop_inplace(df_new_exp, col_list = ['AOD', 'W_LARGE', 'W_TURB', 'u', 'v', 'omega', 'incl_cdnc', 'incl_icnc'])

     # Perform Welch's t-test for each variable
     # ----------------------------------------------------------------
     file_result_welche = os.path.join(paths.p_new_exp, 'result_welchs_test.csv')
     df_result = welch_test_all_var(df_a=df_ref, df_b=df_new_exp,filename_student_test=file_result_welche)


     # print infos
     # -------------------------------------------------------------------
     # print warnings for small p-values
     print_warnings_pvalues(df_result,p_treshold=0.1,new_exp=new_exp)
     print('To see the whole table containing p-values, please the file:{}'.format(file_result_welche))
     print()

     # plot
     # -------------------------------------------------------------------
     plt.plt_var(df_ref,df_new_exp,new_exp)
