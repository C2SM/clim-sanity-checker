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

    def __setattr__(self, name, value):
         raise Exception("This property is read only!")

@begin.start

#def run(exppath='/project/s903/nedavid/plattform_comparison/', expname = 'aerosol_REF_10y', \
#        file_sum = '/project/s903/colombsi/plattform_comparison/Platform_comparison.xlsx',\
#        wrk_dir = '/project/s903/colombsi/plattform_comparison/Sandbox/') :
def run(exppath='/Users/colombsi/Documents/ECHAM-runs/', expname='aerosol_REF_10y',
        file_summary = '/Users/colombsi/Documents/sanity-test-hammoz/Platform_comparison.xlsx',
        wrk_dir = '/Users/colombsi/Documents/Sandbox/'):

    os.chdir(wrk_dir)
    data = table_ref(file_summary)

    print(data.exp)



