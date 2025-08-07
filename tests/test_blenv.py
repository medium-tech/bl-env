import unittest
import shutil
import venv
import os
import re
import sys
from blenv import create_bl_env, find_venv, VENV_SEARCH_PATHS, BlenvConf
from . import TEST_DIR

python_version = f'{sys.version_info.major}.{sys.version_info.minor}'

class TestBlenv(unittest.TestCase):

    def setUp(self):
        # Ensure the test directory is clean before each test
        try:
            shutil.rmtree(TEST_DIR)
        except FileNotFoundError:
            pass
        TEST_DIR.mkdir(parents=True, exist_ok=True)
        os.chdir(TEST_DIR)

    def tearDown(self):
        # Clean up after tests
        os.chdir(TEST_DIR.parent)
        try:
            shutil.rmtree(TEST_DIR)
        except FileNotFoundError:
            pass

    def test_find_venv(self):
        """test find_venv function"""

        # Initially, there should be no venv found

        self.assertIsNone(find_venv())

        # Create venvs in different standard locations and test detection

        for search_path in VENV_SEARCH_PATHS:

            venv.create(TEST_DIR / search_path)
            discovered_venv = find_venv()

            self.assertTrue(discovered_venv is not None)
            venv_path, site_packages_path = discovered_venv

            self.assertTrue(search_path in venv_path)
            self.assertTrue('site-packages' in site_packages_path)
            self.assertTrue(site_packages_path.startswith(venv_path))
            self.assertFalse(venv_path.startswith(site_packages_path))

            self.assertTrue(os.path.exists(venv_path))
            self.assertTrue(os.path.exists(site_packages_path))

            for name in TEST_DIR.iterdir():
                if name.is_dir():
                    shutil.rmtree(name.as_posix())

    def test_setup_no_venv(self):
        self.assertIsNone(find_venv())

        create_bl_env(yes=True)
    
        env_path = TEST_DIR / '.env'
        with open(env_path, 'r') as f:
            content = f.read()
            blender_user_resources = 'BLENDER_USER_RESOURCES=' + str(TEST_DIR / '.blenv/bl')
            python_path = 'PYTHONPATH=' + str(TEST_DIR / '.blenv/venv3.+/lib/python3.+/site-packages')
            self.assertIsNotNone(re.search(blender_user_resources, content))
            self.assertIsNotNone(re.search(python_path, content))

        blenv_yaml_path = TEST_DIR / '.blenv.yaml'
        blenv_yaml = BlenvConf.from_yaml_file(blenv_yaml_path)
        self.assertTrue(isinstance(blenv_yaml, BlenvConf))

        blenv_path = TEST_DIR / '.blenv'
        self.assertTrue(blenv_path.exists())
        self.assertTrue((blenv_path / 'bl/extensions').is_dir())
        self.assertTrue((blenv_path / 'bl/scripts/addons/modules').is_dir())
        self.assertTrue((blenv_path / 'bl/scripts/startup/bl_app_templates_user').is_dir())
        
        self.assertTrue((blenv_path / f'venv{python_version}/bin').is_dir())

    def test_setup_with_existing_venv(self):
        self.assertIsNone(find_venv())

        venv_path = TEST_DIR / '.venv'
        venv.create(venv_path)
        
        create_bl_env(use_venv=str(venv_path), yes=True)

        env_path = TEST_DIR / '.env'
        with open(env_path, 'r') as f:
            content = f.read()
            blender_user_resources = 'BLENDER_USER_RESOURCES=' + str(TEST_DIR / '.blenv/bl')
            python_path = 'PYTHONPATH=' + str(TEST_DIR / '.venv/lib/python3.+/site-packages')
            self.assertIsNotNone(re.search(blender_user_resources, content))
            self.assertIsNotNone(re.search(python_path, content))
            
        blenv_yaml_path = TEST_DIR / '.blenv.yaml'
        blenv_yaml = BlenvConf.from_yaml_file(blenv_yaml_path)
        self.assertTrue(isinstance(blenv_yaml, BlenvConf))

        blenv_path = TEST_DIR / '.blenv'
        self.assertTrue(blenv_path.exists())
        self.assertTrue((blenv_path / 'bl/extensions').is_dir())
        self.assertTrue((blenv_path / 'bl/scripts/addons/modules').is_dir())
        self.assertTrue((blenv_path / 'bl/scripts/startup/bl_app_templates_user').is_dir())

        self.assertTrue((venv_path).is_dir())


    def test_setup_with_existing_venv_custom_path(self):
        self.assertIsNone(find_venv())

        venv_path = TEST_DIR / 'my_venv'
        venv.create(venv_path)

        create_bl_env(use_venv=str(venv_path), yes=True)

        env_path = TEST_DIR / '.env'
        with open(env_path, 'r') as f:
            content = f.read()
            blender_user_resources = 'BLENDER_USER_RESOURCES=' + str(TEST_DIR / '.blenv/bl')
            python_path = 'PYTHONPATH=' + str(TEST_DIR / 'my_venv/lib/python3.+/site-packages')
            self.assertIsNotNone(re.search(blender_user_resources, content))
            self.assertIsNotNone(re.search(python_path, content))

        blenv_yaml_path = TEST_DIR / '.blenv.yaml'
        blenv_yaml = BlenvConf.from_yaml_file(blenv_yaml_path)
        self.assertTrue(isinstance(blenv_yaml, BlenvConf))

        blenv_path = TEST_DIR / '.blenv'
        self.assertTrue(blenv_path.exists())
        self.assertTrue((blenv_path / 'bl/extensions').is_dir())
        self.assertTrue((blenv_path / 'bl/scripts/addons/modules').is_dir())
        self.assertTrue((blenv_path / 'bl/scripts/startup/bl_app_templates_user').is_dir())

        self.assertTrue((venv_path).is_dir())


if __name__ == '__main__':
    unittest.main()
