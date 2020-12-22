import os
import argparse

def write_path(p_raw_files, \
               p_gen = None,\
               p_scripts = None,\
               p_ref_csv_files = None,\
               p_stages = None,\
               p_wrkdir = None,\
               p_time_serie = None,\
               p_f_vars_proc = None,\
               file_paths = 'paths.py'):
    '''
    Function to write the paths used on this machine in an external file.

    Use in terminal:
    python paths_init.py -pr /project/s903/nedavid/plattform_comparison/

    Use by the call of function:
    paths_init.write_path(p_raw_files = '/project/s903/nedavid/plattform_comparison/')

    arguments:
    p_raw_files     :  Path to the raw files of the experiments (mandatory)
    p_gen           :  General path (default : ./)
    p_scripts       :  Path to the scripts (default : ./)
    p_ref_csv_files :  Path to the pool of csv files, one per reference experiment (default: ./ref/echam-hammoz)
    p_out_new_exp   :  Path to the folder for the result of new experiment to analyse (default : ./results_new_exp)
    p_wrkdir        :  Path to the working directory (default : ./wrkdir)
    p_time_serie    :  Path to annual global time series (default : ./wrkdir)
    p_f_vars_proc   :  Path to file containnig variables to process (default : ./variables_to_process)
    file_paths      :  File in which the paths should be written in (output of this function)

    '''


    # definition paths
    if p_gen is None:
        p_gen = os.getcwd()

    if p_scripts is None:
        p_scripts = p_gen

    if p_ref_csv_files is None:
        p_ref_csv_files = os.path.join(p_gen,'ref/echam-hammoz')

    if p_stages is None:
        p_stages = os.path.join(p_gen, 'results_new_exp')

    if p_wrkdir is None:
        p_wrkdir = os.path.join(p_gen,'wrkdir')

    if p_time_serie is None:
        p_time_serie = p_wrkdir

    if p_f_vars_proc is None:
        p_f_vars_proc = os.path.join(p_scripts,'variables_to_process')


    # open the file
    fp=open(file_paths,'w')

    # write out paths
    fp.write('p_raw_files = "{}"\n'.format(p_raw_files))
    fp.write('p_gen = "{}"\n'.format(p_gen))
    fp.write('p_scripts = "{}"\n'.format(p_scripts))
    fp.write('p_ref_csv_files = "{}"\n'.format(p_ref_csv_files))
    fp.write('p_stages = "{}"\n'.format(p_stages))
    fp.write('p_wrkdir = "{}"\n'.format(p_wrkdir))
    fp.write('p_time_serie = "{}"\n'.format(p_time_serie))
    fp.write('p_f_vars_proc = "{}"\n'.format(p_f_vars_proc))


    # close file
    fp.close()

    # create folders
    if not os.path.isdir(p_wrkdir):
        os.mkdir(p_wrkdir)
    if not os.path.isdir(p_stages):
        os.mkdir(p_stages)

    return()

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('--p_raw_files','-pr', dest='p_raw_files', \
                        required=True, \
                        help='Path to the raw files of the new experiments (mandatory)')
    parser.add_argument('--p_gen', dest='p_gen', \
                        default=None, \
                        help='General path (default : ./)')
    parser.add_argument('--p_scripts',dest='p_scripts', \
                        default=None,\
                        help='Path to the scripts (default : ./)')
    parser.add_argument('--p_ref_csv_files',dest='p_ref_csv_files', \
                        default=None, \
                        help='Path to the pool of csv files, one per reference experiment (default: ./ref/echam-hammoz)')
    parser.add_argument('--p_stages',dest='p_stages', \
                        default=None, \
                        help='Path to the folder to store results of the different processing stages (default : ./results_new_exp)')
    parser.add_argument('--p_wrkdir', dest='p_wrkdir', \
                        default=None, \
                        help='Path to the working directory (default : ./wrkdir)')
    parser.add_argument('--p_time_serie',dest='p_time_serie', \
                        default=None, \
                        help='Path to annual global time series (default : ./wrkdir)')
    parser.add_argument('--p_f_vars_proc',dest='p_f_vars_proc',\
                        default=None, \
                        help='Path to file containnig variables to process (default : ./variables_to_process)')
    parser.add_argument('--file_paths', dest='file_paths', \
                        default='paths.py', \
                        help='File in which the paths should be written in')

    args = parser.parse_args()

    write_path(p_raw_files     = args.p_raw_files, \
               p_gen           = args.p_gen, \
               p_scripts       = args.p_scripts, \
               p_ref_csv_files = args.p_ref_csv_files, \
               p_stages        = args.p_stages, \
               p_wrkdir        = args.p_wrkdir,\
               p_time_serie    = args.p_time_serie,\
               p_f_vars_proc   = args.p_f_vars_proc,\
               file_paths      = args.file_paths)
