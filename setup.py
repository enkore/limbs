#!/usr/bin/env python3

import sys

from setuptools import setup

DESCRIPTION = """like mime, but simpler - a simple, human-readable file format

Simple I/O to flat text files with a header (composed of fields) and a body (arbitrary bytes).
Ideal for no-hassle storage of some metadata and some large data that doesn't fit nicely into
things like JSON (which becomes really hard to edit in a text editor if there's a 2 MB blob of
numbers somewhere in it)."""

setup(name="limbs", version="0.4",
      description=DESCRIPTION,
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
