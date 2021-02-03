import testsuite.utils as utils
import os

def test_fldcor_embed():

    input_dir = 'testsuite/data'
    exp_name = 'run_emded'
    files_generated = []

    os.makedirs('stages',exist_ok=True)

    standard_postproc = 'stages/standard_postproc_rmse_{}.nc'\
        .format(exp_name)

    files_generated.append(standard_postproc)

    file_with_ftp_link = ('testsuite/variables_to_process/'
                          'rmse/ftp_fake_postproc.txt')

    cmd = ('wget --quiet --input-file={} '
           '--output-document={}'.format(file_with_ftp_link,
                                         standard_postproc))
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'Could not download reference from ftp-server'

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'

    cmd = 'python sanity_test.py -v -e {} -t rmse  \
        --p_ref_csv_files testsuite/ref --f_vars_to_extract \
        vars_rmse_test.csv -ts'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    utils.delete_data(files_generated)

    assert status == 0, 'sanity_test.py failed'


def test_fldcor_chained():

    input_dir = 'testsuite/data'
    exp_name = 'run_chained'
    files_generated = []

    os.makedirs('stages',exist_ok=True)

    standard_postproc = 'stages/standard_postproc_rmse_{}.nc'\
        .format(exp_name)

    files_generated.append(standard_postproc)

    file_with_ftp_link = ('testsuite/variables_to_process/rmse'
                          '/ftp_fake_postproc.txt')

    cmd = ('wget --quiet --input-file={} '
           '--output-document={}'.format(file_with_ftp_link,
                                         standard_postproc))
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'Could not download reference from ftp-server'

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'

    cmd = 'python process_data.py -v -e {} -t rmse \
        --f_vars_to_extract vars_rmse_test.csv '.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'process_data.py failed'

    cmd = 'python perform_test.py -v -e {} -t rmse \
        --p_ref_csv_files testsuite/ref --f_vars_to_extract \
        vars_rmse_test.csv -ts'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    utils.delete_data(files_generated)

    assert status == 0, 'perform_test.py failed'
