# shared-dependencies/setup.py
from setuptools import setup, find_packages

# Carica le dipendenze comuni dal file
with open("common_dependencies.txt") as f:
    common_dependencies = [line.strip() for line in f]

setup(
    name='shared-dependencies',
    version='0.1',
    packages=find_packages(),
    install_requires=common_dependencies,
)
