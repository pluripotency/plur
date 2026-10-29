import unittest
import os
from mini import misc
from plur import session_wrap
from plur import base_shell

test_doc = """This is test line 1
This is test line 2
This is test line 3
This is test line 4
"""


class TestShell(unittest.TestCase):
    def setUp(self):
        self.test_doc_path = '/tmp/test_doc.txt'
        misc.open_write(self.test_doc_path, test_doc)

    def test_capture(self):
        @session_wrap.bash()
        def func(session):
            capture = base_shell.run(session, 'cat ' + self.test_doc_path)
            self.assertEqual(capture.splitlines()[2:-1], test_doc.splitlines())
        func()

    def tearDown(self):
        os.remove(self.test_doc_path)

if __name__ == '__main__':
    unittest.main()
