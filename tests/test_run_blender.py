import unittest
import os
import time
import subprocess
import signal
from pathlib import Path
from blenv import run_blender_from_env

this_dir = Path(__file__).parent
examples_dir = this_dir.parent / 'examples'
SLEEP_TIME = 3

class TestRunBlender(unittest.TestCase):

    def tearDown(self):
        os.chdir(this_dir)

    def test_hello_extension_run_blender_debug(self):
        os.chdir(examples_dir / 'bl-hello-extension')

        result = run_blender_from_env(debug=True)
        self.assertIsInstance(result, dict)
        self.assertIn('popen_args', result)
        self.assertIn('popen_kwargs', result)

        self.assertIn('blender', result['popen_args'][0].lower())
        self.assertEqual(result['popen_args'][1], '--addons')
        self.assertEqual(result['popen_args'][2], 'object_cursor_array')

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

    def test_hello_extension_run_blender_custom_args(self):
        os.chdir(examples_dir / 'bl-hello-extension')

        result = run_blender_from_env(debug=True, args=['arg1', 'arg2'])
        self.assertIsInstance(result, dict)
        self.assertIn('popen_args', result)
        self.assertIn('popen_kwargs', result)

        self.assertIn('blender', result['popen_args'][0].lower())
        self.assertEqual(result['popen_args'][1], 'arg1')
        self.assertEqual(result['popen_args'][2], 'arg2')

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

    def test_hello_extension_run_blender(self):
        os.chdir(examples_dir / 'bl-hello-extension')

        args = ['python', '-m', 'blenv', 'run']

        process = subprocess.Popen(
            args
        )
        
        time.sleep(SLEEP_TIME)   # sleep for a bit so we know it didn't exit immediately

        # send ctl-c twiced to trigger exit
        os.kill(process.pid, signal.SIGINT)
        time.sleep(.1)
        os.kill(process.pid, signal.SIGINT)

        process.wait()

        self.assertEqual(process.returncode, 0)

    def test_hello_app_template_run_blender_debug(self):
        os.chdir(examples_dir / 'bl-hello-app-template')

        result = run_blender_from_env(debug=True)
        self.assertIsInstance(result, dict)
        self.assertIn('popen_args', result)
        self.assertIn('popen_kwargs', result)

        self.assertIn('blender', result['popen_args'][0].lower())
        self.assertEqual(result['popen_args'][1], '--app-template')
        self.assertEqual(result['popen_args'][2], 'hello_app_template')

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

    def test_hello_app_template_run_blender(self):
        os.chdir(examples_dir / 'bl-hello-app-template')

        args = ['python', '-m', 'blenv', 'run']

        process = subprocess.Popen(
            args
        )
        
        time.sleep(SLEEP_TIME)   # sleep for a bit so we know it didn't exit immediately

        # send ctl-c twiced to trigger exit
        os.kill(process.pid, signal.SIGINT)
        time.sleep(.1)
        os.kill(process.pid, signal.SIGINT)

        process.wait()

        self.assertEqual(process.returncode, 0)