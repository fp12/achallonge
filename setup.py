from setuptools import setup, find_packages
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


setup(name='achallonge',
      author='Fabien Poupineau (fp12)',
      url='https://github.com/fp12/achallonge',
      version='1.1.0',
      packages=find_packages(),
      license='MIT',
      description='A python library to use the Challonge API',
      long_description=readme,
      include_package_data=True,
      install_requires=requirements,
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
      keywords='challonge tournament match',
      )
