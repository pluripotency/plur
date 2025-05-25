import unittest
from plur import spawn
from plur.output_methods import success, send_control


class TestSpawn(unittest.TestCase):
    def test_pexpect_spawn_timeout(self):
        instance = spawn.Spawn()
        instance.set_timeout(1)
        instance.action_handler('sleep 10', method_type=None)
        result = instance.child.expect([spawn.pexpect.TIMEOUT, spawn.pexpect.EOF])
        instance.close()
        self.assertEqual(result, 0)

    def test_pexpect_spawn_eof(self):
        instance = spawn.Spawn()
        instance.set_timeout(1)
        instance.action_handler('echo', method_type=None)
        result = instance.child.expect([spawn.pexpect.TIMEOUT, spawn.pexpect.EOF])
        instance.close()
        self.assertEqual(result, 1)


class TestSpawnSend(unittest.TestCase):
    def setUp(self):
        self.spawn = spawn.Spawn()

    def tearDown(self) -> None:
        if self.spawn:
            self.spawn.close()

    def test_spawn_sendline(self):
        result = self.spawn.do([
            'echo test',
            [
                ['test', success, 'echo success']
            ],
            None
        ])
        self.assertEqual(result, 'echo success')

    def test_spawn_send(self):
        result = self.spawn.do([
            'echo test\n',
            [
                ['test', success, 'echo success']
            ],
            None
        ])
        self.assertEqual(result, 'echo success')

    def test_spawn_sendcontrol(self):
        linux_prompt = r'\$ '
        self.spawn.do([
            'bash',
            [
                [linux_prompt, success, True]

            ],
            None
        ])
        result = self.spawn.do([
            'sleep 10',
            [
                [r'sleep', send_control, 'c']
                , [linux_prompt, success, 'ctrl c success']

            ],
            None
        ])
        self.assertEqual(result, 'ctrl c success')

    # def test_spawn_unknown_method(self):
    #     seq1 = [
    #         'test',
    #         [
    #             ['something', spawn.success, 'something success']
    #         ],
    #         'unknown method'
    #     ]
    #     with self.assertRaises(SystemExit) as cm:
    #         result = self.spawn.do(seq1)
    #     self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
