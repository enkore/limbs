#!/usr/bin/env python3

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(name="limbs", version="0.1",
      description="like mime but simpler - a simple, human-readable format",
      url="http://github.com/enkore/limbs/",
      author="Marian Beermann", author_email="public@enkore.de",
      license="MIT",
      py_modules=["limbs"],

      # py.test integration
      tests_require=['pytest'],
      cmdclass = {'test': PyTest},
      )
