#!/usr/bin/env python

from setuptools import setup

with open("requirements.txt") as file:
    REQUIREMENTS = [line for line in file if (line != "") | (~line.startswith("#"))]

setup(
    name='runtime',
    version='1.0',
    description='Inovalife runtime',
    author='Marcelo Tournier',
    author_email='marcelo@inova.life',
    url='https://github.com/marcelotournier/colab',
    packages=['runtime'],
    install_requires=REQUIREMENTS
    )
