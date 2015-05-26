#!/usr/bin/env python3

import sys

from setuptools import setup

setup(name="limbs", version="0.2",
      description="like mime but simpler - a simple, human-readable format",
      url="http://github.com/enkore/limbs/",
      author="Marian Beermann", author_email="public@enkore.de",
      classifiers=[
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Software Development :: Libraries",
      ],
      py_modules=["limbs"],
      )
