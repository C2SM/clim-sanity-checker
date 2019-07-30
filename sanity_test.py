# Script to test sanity of a n HAMMOZ run
# C.Siegenthaler, 2019


from shell_interactions import sys_cmd
import begin
import os
import pandas as pd

wk_dir = '/project/s903/colombsi/plattform_comparison/Sandbox/'

def cdo_process(filename) :
    return()


@begin.start

def run(path='/project/s903/nedavid/plattform_comparison/', expname = 'aerosol_REF_10y', \
        file_sum = '/project/s903/colombsi/plattform_comparison/Platform_comparison.xlsx'):

    os.chdir(wk_dir)


    
