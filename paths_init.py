# standard modules
import os
import argparse

# modules of sanity checker
import utils

def write_path(p_raw_files, \
               p_ref_csv_files,\
               p_stages,\
               p_wrkdir,\
               p_f_vars_proc):

    # make all paths absolute
    p_raw_files = utils.abs_path(p_raw_files)
    p_ref_csv_files = utils.abs_path(p_ref_csv_files)
    p_stages = utils.abs_path(p_stages)
    p_wrkdir = utils.abs_path(p_wrkdir)
    p_f_vars_proc = utils.abs_path(p_f_vars_proc)

    # open the file
    fp=open('paths.py','w')

    # write out paths
    fp.write('p_raw_files = "{}"\n'.format(p_raw_files))
    fp.write('p_ref_csv_files = "{}"\n'.format(p_ref_csv_files))
    fp.write('p_stages = "{}"\n'.format(p_stages))
    fp.write('p_wrkdir = "{}"\n'.format(p_wrkdir))
    fp.write('p_f_vars_proc = "{}"\n'.format(p_f_vars_proc))

    # close file
    fp.close()

    return()

if __name__ == '__main__':

    # parsing arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--p_raw_files','-pr', dest='p_raw_files', \
                        required=True, \
                        help='Path to the raw files of the new experiments (mandatory)')

    parser.add_argument('--p_ref_csv_files',dest='p_ref_csv_files', \
                        default='ref/echam-hammoz', \
                        help='Relative or absolute path to the pool of reference csv-files')

    parser.add_argument('--p_stages',dest='p_stages', \
                        default='stages', \
                        help='Relative or absolute path to the folder to store results of the different processing stages (needs disk space)')

    parser.add_argument('--p_wrkdir', dest='p_wrkdir', \
                        default='wrkdir', \
                        help='Relative or absolute path to the working directory (needs disk space)')

    parser.add_argument('--p_f_vars_proc',dest='p_f_vars_proc',\
                        default='variables_to_process', \
                        help='Relative and absolute path to file containig variables to process')

    args = parser.parse_args()

    write_path(p_raw_files     = args.p_raw_files, \
               p_ref_csv_files = args.p_ref_csv_files, \
               p_stages        = args.p_stages, \
               p_wrkdir        = args.p_wrkdir,\
               p_f_vars_proc   = args.p_f_vars_proc)
