"""Setup script for odin_workshop python package."""

import sys
from setuptools import setup, find_packages
import versioneer

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='workshop',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='ODIN Workshop',
      url='https://github.com/stfc-aeg/odin-workshop',
      author='Tim Nicholls',
      author_email='tim.nicholls@stfc.ac.uk',
      packages=find_packages(),
      install_requires=required,
      zip_safe=False,
)
