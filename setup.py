from setuptools import setup

setup(
    name='python-utility-scripts',
    version='0.1',
    description='Some utility-scripts for python.',
    url='https://github.com/trivernis/python-utility-scripts',
    author='trivernis',
    license='GPLv3',
    packages=['python-utility-scripts'],
    install_requires=[
        'bs4',
        'lxml'
    ],
    zip_safe=False)
