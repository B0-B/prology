from json import load
from setuptools import setup, find_packages
from os import system

def install():

    # read version.json and convert to dictionary for the package body
    with open("version.json", "r") as f:
        body = load(f)
    
    # run the setup
    setup(
        name = body['name'],
        version = body['version'],
        packages = find_packages(),
        author = body['author'],
        author_email = body['author_email'],
        description = body['description'],
        url = body['url'],
        install_requires = body['dependencies'].split(';'),
    )

if __name__ == "__main__":
    install()