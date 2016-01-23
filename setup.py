#!/usr/bin/env python


from glob import glob


from setuptools import setup, find_packages


def parse_requirements(filename):
    with open(filename, "r") as f:
        for line in f:
            if line and line[:2] not in ("#", "-e"):
                yield line.strip()


setup(
    name="js-lang",
    description="An experimental JavaScript Interpreter",
    long_description=open("README.rst", "r").read(),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="https://github.com/prologic/js-lang",
    download_url="https://github.com/prologic/js-lang/releases",
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Assemblers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Interpreters",
    ],
    license="MIT",
    keywords="pypy rpython javascript interpreter js",
    platforms="POSIX",
    packages=find_packages("."),
    include_package_data=True,
    install_requires=list(parse_requirements("requirements.txt")),
    scripts=glob("tools/*"),
    entry_points={
        "console_scripts": [
            "js=js.main:entrypoint",
        ]
    },
    test_suite="tests.main.main",
    zip_safe=False,
    use_scm_version={
        "write_to": "js/version.py",
    },
    setup_requires=[
        "setuptools_scm"
    ],
)
