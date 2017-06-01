DEL /Q dist\* 
CALL venv\Scripts\activate.bat
python setup.py bdist_wheel sdist
twine upload dist\* --config-file .pypirc