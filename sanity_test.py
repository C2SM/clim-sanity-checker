# Script to test sanity of a n HAMMOZ run
# C.Siegenthaler, 2019


from shell_interactions import sys_cmd
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

#def run(exppath='/project/s903/nedavid/plattform_comparison/', expname = 'aerosol_REF_10y', \
#        file_sum = '/project/s903/colombsi/plattform_comparison/Platform_comparison.xlsx',\
#        wrk_dir = '/project/s903/colombsi/plattform_comparison/Sandbox/') :
def run(exppath='/Users/colombsi/Documents/ECHAM-runs/', expname='aerosol_REF_10y',
        file_summary = '/Users/colombsi/Documents/sanity-test-hammoz/Platform_comparison.xlsx',
        wrk_dir = '/Users/colombsi/Documents/Sandbox/sanity_test'):

    # prepare working directory
    os.makedirs(wrk_dir,exist_ok=True)
    os.chdir(wrk_dir)

    # data of reference experiments
    data_ref_file = table_ref(file_summary)

    # global mean new experiment
    p_globmean_newexp = os.path.join(exppath, expname , 'Data/analysis_{}_2003-2012.txt'.format(expname))
    data_newexp_glob = pd.read_csv(p_globmean_newexp, sep='\s+', header=1)

    # standard deviation new experiment
    tmp_timeser_newexp = p_globmean_newexp.replace('analysis', 'timeser').rstrip('.txt')
    p_timeser_newexp = os.path.join(wrk_dir, (os.path.basename(tmp_timeser_newexp) + '.txt'))
    # compute std deviation
    sys_cmd('cdo infov -timstd {}.nc > {}'.format(tmp_timeser_newexp, p_timeser_newexp))
    data_newexp_std = pd.read_csv(p_timeser_newexp, sep=' : ', usecols=[2,3], skiprows = [0], names = ['std','name'])

    data_newexp_std = data_newexp_std.reindex(columns=['name','std'])
    print(data_newexp_std)
#    print(data_newexp_glob)



