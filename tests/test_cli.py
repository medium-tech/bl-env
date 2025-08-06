import unittest
from blenv.__main__ import parser


class TestCLI(unittest.TestCase):

    def test_create_no_venv(self):
        args = parser().parse_args(['create'])
        self.assertEqual(args.command, 'create')
        self.assertIsNone(args.venv)

    def test_create_with_venv(self):
        args = parser().parse_args(['create', '--venv', '/path/to/venv'])
        self.assertEqual(args.command, 'create')
        self.assertEqual(args.venv, '/path/to/venv')

    def test_setup(self):
        args = parser().parse_args(['setup'])
        self.assertEqual(args.command, 'setup')

    def test_run_default(self):
        args = parser().parse_args(['run'])
        self.assertEqual(args.command, 'run')
        self.assertEqual(args.env_name, 'default')
        self.assertFalse(args.debug)
        self.assertIsNone(args.args)

    def test_run_with_env(self):
        args = parser().parse_args(['run', 'my-env'])
        self.assertEqual(args.command, 'run')
        self.assertEqual(args.env_name, 'my-env')
        self.assertFalse(args.debug)
        self.assertIsNone(args.args)

    def test_run_with_debug(self):
        args = parser().parse_args(['run', '--debug'])
        self.assertEqual(args.command, 'run')
        self.assertEqual(args.env_name, 'default')
        self.assertTrue(args.debug)
        self.assertIsNone(args.args)

    def test_run_with_env_and_debug(self):
        args = parser().parse_args(['run', 'my-env', '--debug'])
        self.assertEqual(args.command, 'run')
        self.assertEqual(args.env_name, 'my-env')
        self.assertTrue(args.debug)
        self.assertIsNone(args.args)

    def test_run_with_args(self):
        args = parser().parse_args(['run', '--args', 'arg1', 'arg2'])
        self.assertEqual(args.command, 'run')
        self.assertEqual(args.env_name, 'default')
        self.assertFalse(args.debug)
        self.assertEqual(args.args, ['arg1', 'arg2'])

    def test_run_with_env_debug_and_args(self):
        args = parser().parse_args(['run', 'my-env', '--debug', '--args', 'arg1', 'arg2'])
        self.assertEqual(args.command, 'run')
        self.assertEqual(args.env_name, 'my-env')
        self.assertTrue(args.debug)
        self.assertEqual(args.args, ['arg1', 'arg2'])

if __name__ == '__main__':
    unittest.main()
