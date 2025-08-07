import unittest
import shutil
import venv
import os
from blenv import find_venv, VENV_SEARCH_PATHS
from . import TEST_DIR


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

        

if __name__ == '__main__':
    unittest.main()
