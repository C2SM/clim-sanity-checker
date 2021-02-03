import testsuite.utils as utils

'''
The following picky coding rules are ignored:

############# ERROR CODES ####################

  E265: block comment should start with '#'
  E201: whitespace after '('
  E221: multiple spaces before operator
  E231: missing whitespace after ',' ';' or ':'
  E241: multiples spaces after ','
  E722: do not use bare except, specify exception instead
  E731: do not assign a lambda expression, use a def 
  E225 missing whitespace around operator

############# WARNINGS #######################

  W291: trailing whitespace
  W504: line break after binary operator

'''


def test_main():
    cmd = 'python testsuite/pycodestyle.py \
            --exclude=prepare_csvfiles_ref_echam.py \
            --ignore=E265,W291,E201,E221,E231,E241,E722,W504 *.py'
    status, _ =utils.shell_cmd(cmd)
    assert status == 0, 'Violations of Pep-8-standard found!'


def test_lib():
    cmd = 'python testsuite/pycodestyle.py --exclude=paths.py \
            --ignore=E265,W291,E201,E221,E231,E241,E722,W504,E731 \
            lib/*.py'
    status, _ =utils.shell_cmd(cmd)
    assert status == 0, 'Violations of Pep-8-standard found!'


def test_testsuite():
    cmd = 'python testsuite/pycodestyle.py \
            --ignore=E225,E265,W291,E201,E221,E231,E241,E722,W504 \
            testsuite/*.py'
    status, _ =utils.shell_cmd(cmd)
    assert status == 0, 'Violations of Pep-8-standard found!'
