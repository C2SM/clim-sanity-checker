import testsuite.utils as utils

def test_emi_embed():

    input_dir = 'testsuite/data'
    exp_name = 'run_embed'

    files_generated = utils.generate_data(input_dir,exp_name,'emi_A','SO2')
    files_generated.extend(utils.generate_data(input_dir,exp_name,'emi_B','CO2'))

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python sanity_test.py -v -e {} -t emi --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_emi_test.csv --spinup 0 -c -ts'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    utils.delete_data(files_generated)

    assert status == 0, 'sanity_test.py failed'


def test_emi_chained():

    input_dir = 'testsuite/data'
    exp_name = 'run_chained'

    files_generated = utils.generate_data(input_dir,exp_name,'emi_A','SO2')
    files_generated.extend(utils.generate_data(input_dir,exp_name,'emi_B','CO2'))

    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python process_data.py -v -e {} -t emi --f_vars_to_extract vars_emi_test.csv --spinup 0 -c'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'process_data.py failed'

    cmd = 'python perform_test.py -v -e {} -t emi --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_emi_test.csv -ts'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    utils.delete_data(files_generated)

    assert status == 0, 'perform_test.py failed'
