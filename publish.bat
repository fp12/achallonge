rm -q dist\* 
python setup.py bdist_wheel sdist
twine upload dist\* --config-file .pypirc