import testsuite.utils as utils

#def test_fldcor_embed():
#
#    input_dir = 'testsuite/data'
#    exp_name = 'run_emded'
#    stages = 'stages'
#    ref_name = 'ref_fldcor.nc'
#
#    files_generated = utils.generate_identical_data(input_dir,exp_name,'fldcor_A','SO2')
#    files_generated.extend(utils.generate_identical_data(input_dir,exp_name,'fldcor_B','T2M'))
#    files_generated.extend(utils.generate_ref(stages,ref_name,['SO2','T2M']))
#
#    cmd = 'python paths_init.py -pr {} -ts'.format(input_dir)
#    status, _ =utils.shell_cmd(cmd)
#
#    assert status == 0, 'paths_init.py failed'
#    
#    cmd = 'python sanity_test.py -v -e {} -t fldcor --f_pattern_ref stages/{} --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_fldcor_test.csv -c -ts'.format(exp_name,ref_name)
#    print(cmd)
#
#    status, _ =utils.shell_cmd(cmd)
#
#    assert status == 0, 'sanity_test.py failed'
#
#    utils.delete_data(files_generated)

#def test_fldcor_chained():
#
#    input_dir = 'testsuite/data'
#    exp_name = 'fldcor'
#
#    files_generated = utils.generate_data(input_dir,exp_name,'fldcor_A','SO2')
#    files_generated.extend(utils.generate_data(input_dir,exp_name,'fldcor_B','T2M'))
#
#    cmd = 'python paths_init.py -pr {}'.format(input_dir)
#    status, _ =utils.shell_cmd(cmd)
#
#    assert status == 0, 'paths_init.py failed'
#    
#    cmd = 'python process_data.py -v -e {} -t pattern_correlation --f_vars_to_extract vars_fldcor_test.csv -c'.format(exp_name)
#
#    status, _ =utils.shell_cmd(cmd)
#
#    assert status == 0, 'process_data.py failed'
#
#    cmd = 'python perform_test.py -v -e {} -t pattern_correlation  --p_ref_csv_files testsuite/ref --f_vars_to_extract vars_fldcor_test.csv -ts'.format(exp_name)
#
#    status, _ =utils.shell_cmd(cmd)
#
#    assert status == 0, 'perform_test.py failed'
#
#    utils.delete_data(files_generated)
