import testsuite.utils as utils

def test_welch_embed():
    input_dir = 'testsuite/data'
    exp_name = 'welch'

    files_generated = utils.generate_data(input_dir,exp_name,'2d_A','TSURF')
    files_generated.extend(utils.generate_data(input_dir,exp_name,'2d_B','T2M'))

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ = utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python sanity_test.py -e {} -t welchstest --spinup 0 --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_welchs_test.csv -c -ts'.format(exp_name)

    status, _ = utils.shell_cmd(cmd)

    utils.delete_data(files_generated)
    assert status == 0, 'sanity_test.py failed'


def test_welch_chained():
    input_dir = 'testsuite/data'
    exp_name = 'welch'

    files_generated = utils.generate_data(input_dir,exp_name,'2d_A','TSURF')
    files_generated.extend(utils.generate_data(input_dir,exp_name,'2d_B','T2M'))

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ = utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python process_data.py -e {} -t welchstest --spinup 0 --f_vars_to_extract vars_welchs_test.csv -c'.format(exp_name)

    status, _ = utils.shell_cmd(cmd)

    assert status == 0, 'process_data.py failed'

    cmd = 'python perform_test.py  -e {} -t welchstest  --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_welchs_test.csv -ts'.format(exp_name)

    status, _ = utils.shell_cmd(cmd)

    utils.delete_data(files_generated)

    assert status == 0, 'perform_test.py failed'
