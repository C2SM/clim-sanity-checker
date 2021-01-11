import testsuite.utils as utils

def test_emi_embed():

    input_dir = 'testsuite/data'
    exp_name = 'emi'

    files_generated = utils.generate_data(input_dir,exp_name,'emi_A','SO2')
    files_generated.extend(utils.generate_data(input_dir,exp_name,'emi_B','CO2'))

    cmd = 'python paths_init.py -pr {}'.format(input_dir)
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python sanity_test.py -v -e {} -t emissions --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_emi_test.csv -c -ts'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'sanity_test.py failed'

    utils.delete_data(files_generated)

def test_emi_chained():

    input_dir = 'testsuite/data'
    exp_name = 'emi'

    files_generated = utils.generate_data(input_dir,exp_name,'emi_A','SO2')
    files_generated.extend(utils.generate_data(input_dir,exp_name,'emi_B','CO2'))

    cmd = 'python paths_init.py -pr {}'.format(input_dir)
    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'paths_init.py failed'
    
    cmd = 'python process_data.py -v -e {} -t emissions --f_vars_to_extract vars_emi_test.csv -c'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'process_data.py failed'

    cmd = 'python perform_test.py -v -e {} -t emissions  --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_emi_test.csv -ts'.format(exp_name)

    status, _ =utils.shell_cmd(cmd)

    assert status == 0, 'perform_test.py failed'

    utils.delete_data(files_generated)
