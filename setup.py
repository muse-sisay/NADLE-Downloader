from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f :
    install_requires=[ x for x in f.readlines() if '#' not in x ]

setup(
    name='nadel',
    version='1.0',
    description=
    'A simple python module for downloading books from http://ndl.ethernet.edu.et/',
    author='Muse Sisay',
    #packages=['nadle'],
    packages=find_packages('nadle'),
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        nadle=nadle.nadle_dl:cli
    ''',
)
