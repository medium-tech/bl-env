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
        self.assertEqual(result['popen_args'][1], '--python-use-system-env')
        self.assertEqual(result['popen_args'][2], '--addons')
        self.assertEqual(result['popen_args'][3], 'object_cursor_array')

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

    def test_hello_extension_override_args(self):
        os.chdir(examples_dir / 'bl-hello-extension')

        result = run_blender_from_env(debug=True, override_args=['one', 'two', 'three'])
        self.assertIsInstance(result, dict)
        self.assertIn('popen_args', result)
        self.assertIn('popen_kwargs', result)

        self.assertIn('blender', result['popen_args'][0].lower())
        self.assertEqual(result['popen_args'][1], 'one')
        self.assertEqual(result['popen_args'][2], 'two')
        self.assertEqual(result['popen_args'][3], 'three')
        self.assertEqual(len(result['popen_args']), 4)

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

    def test_hello_extension_extend_args(self):
        os.chdir(examples_dir / 'bl-hello-extension')

        result = run_blender_from_env(debug=True, extend_args=['one', 'two', 'three'])
        self.assertIsInstance(result, dict)
        self.assertIn('popen_args', result)
        self.assertIn('popen_kwargs', result)

        self.assertIn('blender', result['popen_args'][0].lower())
        self.assertEqual(result['popen_args'][1], '--python-use-system-env')
        self.assertEqual(result['popen_args'][2], '--addons')
        self.assertEqual(result['popen_args'][3], 'object_cursor_array')
        self.assertEqual(result['popen_args'][4], 'one')
        self.assertEqual(result['popen_args'][5], 'two')
        self.assertEqual(result['popen_args'][6], 'three')
        self.assertEqual(len(result['popen_args']), 7)

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

    def test_hello_extension_run_blender_custom_args(self):
        os.chdir(examples_dir / 'bl-hello-extension')

        result = run_blender_from_env('custom_args', debug=True)
        self.assertIsInstance(result, dict)
        self.assertIn('popen_args', result)
        self.assertIn('popen_kwargs', result)

        self.assertIn('blender', result['popen_args'][0].lower())

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

        self.assertEqual(result['popen_args'][1], '--background')
        self.assertEqual(result['popen_args'][2], '--python-expr')
        python_cmd = "import bpy; print(f'Custom Args Environment: Blender version {bpy.app.version_string}')"
        self.assertEqual(result['popen_args'][3], python_cmd)
        self.assertEqual(len(result['popen_args']), 4)

        args = ['python', '-m', 'blenv', 'run', 'custom_args']

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # should exist immediately but if it doesn't, kill process
        time.sleep(SLEEP_TIME)

        if process.poll() is None:
            os.kill(process.pid, signal.SIGINT)
            time.sleep(.1)
            os.kill(process.pid, signal.SIGINT)
            self.fail('Process did not exit immediately as expected')

        process.wait()

        self.assertEqual(process.returncode, 0)

        # get std output
        stdout, stderr = process.communicate()
        text = 'Custom Args Environment: Blender version '
        self.assertIn(text, stdout.decode())

    def test_hello_extension_run_blender(self):
        os.chdir(examples_dir / 'bl-hello-extension')

        args = ['python', '-m', 'blenv', 'run']

        process = subprocess.Popen(args)
        
        time.sleep(SLEEP_TIME)   # sleep for a bit so we know it didn't exit immediately

        self.assertIsNone(process.poll())

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
        self.assertEqual(result['popen_args'][1], '--python-use-system-env')
        self.assertEqual(result['popen_args'][2], '--app-template')
        self.assertEqual(result['popen_args'][3], 'hello_app_template')

        self.assertEqual(result['popen_kwargs']['env_file'], '.env')
        self.assertTrue(result['popen_kwargs']['env_inherit'])
        self.assertTrue(result['popen_kwargs']['env_override'])

    def test_hello_app_template_run_blender(self):
        os.chdir(examples_dir / 'bl-hello-app-template')

        args = ['python', '-m', 'blenv', 'run']

        process = subprocess.Popen(args)
        
        time.sleep(SLEEP_TIME)   # sleep for a bit so we know it didn't exit immediately

        self.assertIsNone(process.poll())

        # send ctl-c twiced to trigger exit
        os.kill(process.pid, signal.SIGINT)
        time.sleep(.1)
        os.kill(process.pid, signal.SIGINT)

        process.wait()

        self.assertEqual(process.returncode, 0)

    def test_version(self):
        os.chdir(examples_dir / 'bl-hello-app-template')

        args = ['python', '-m', 'blenv', 'version']

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        self.assertEqual(process.returncode, 0)
        self.assertEqual(stderr, b'')

        output = stdout.decode()
        
        self.assertIn('Python version:', output)
        self.assertIn('Blenv version:', output)
        self.assertIn('Blender python:', output)
        
        self.assertTrue(output.count('Blender') >= 3)
