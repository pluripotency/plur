import unittest
import os
import re
from plur import base_node
from plur import base_shell
from plur import session


class TestSession(unittest.TestCase):
    def setUp(self):
        log_dir = '/tmp/plur3_test_session_log'
        log_params = {
            'log_dir': log_dir,
            'enable_stdout': False,
            'output_log_file_path': f'{log_dir}/output.log',
            'dont_truncate': False,
            'debug_color': True,
            'debug_log_file_path': f'{log_dir}/debug.log',
        }
        test_txt_path = '/tmp/test_plur3_session.txt'

        with open(test_txt_path, 'w') as f:
            f.write('This is test')
        self.test_txt_path = test_txt_path
        self.session = session.Session(base_node.Me(), log_params).bash()

    def tearDown(self) -> None:
        self.session.close()
        os.unlink(self.test_txt_path)

    def test_session(self):
        result = base_shell.run(self.session, f'cat {self.test_txt_path}')
        searched = re.search('This is test', result)
        if searched:
            res = True
        else:
            res = False
        self.assertEqual(res, True)


if __name__ == '__main__':
    unittest.main()