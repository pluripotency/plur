import unittest
import os
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
        self.test_doc = test_doc
        @session_wrap.bash()
        def func(session):
            base_shell.here_doc(session, self.test_doc_path, self.test_doc.splitlines())
            with open(self.test_doc_path, 'r') as f:
                read_doc = f.read()
            self.assertEqual(read_doc, test_doc)
        func()

    def test_capture(self):
        @session_wrap.bash()
        def func(session):
            capture = base_shell.run(session, 'cat ' + self.test_doc_path)
            # captured last line is prompt head from child.before prompt match
            self.assertEqual(capture.splitlines(), self.test_doc.splitlines())
        func()

    def tearDown(self):
        os.remove(self.test_doc_path)

if __name__ == '__main__':
    unittest.main()
