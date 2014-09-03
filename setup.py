#!/usr/bin/env python


from subprocess import check_output


from setuptools import find_packages, setup


setup(
    name="js",
    version=check_output("hg id -i", shell=True),
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "js=js.main:entrypoint"
        ]
    }
)
