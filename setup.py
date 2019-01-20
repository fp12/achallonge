from setuptools import setup, find_packages
import re
import os


on_rtd = os.getenv('READTHEDOCS') == 'True'

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

if on_rtd:
    requirements.append('sphinxcontrib-napoleon')

readme = ''
with open('README.md') as f:
    readme = f.read()

version = ''
with open('challonge/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(name='achallonge',
      version=version,

      description='A python library to use the Challonge API',
      long_description=readme,
      long_description_content_type="text/markdown",

      license='MIT',

      author='Fabien Poupineau (fp12)',
      url='https://github.com/fp12/achallonge',

      packages=find_packages(),
      install_requires=requirements,
      extras_require={
        'speed':  ['cchardet', 'aiodns']
      },

      include_package_data=True,

      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ],
      keywords=['challonge',  'tournament', 'match']
)
