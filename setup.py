#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
Namespace packaging here

# Make sure we declare an __init__.py file as namespace holder in the package root containing the following

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
"""

import codecs
import os

import pkg_resources
import setuptools


def get_metadata(package_file):
    """
    Read metadata from pacakge file
    """

    def _read(_package_file):
        here = os.path.abspath(os.path.dirname(__file__))
        with codecs.open(os.path.join(here, _package_file), 'r') as fp:
            return fp.read()

    _metadata = {}

    for line in _read(package_file).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            _metadata['version'] = line.split(delim)[1]
        if line.startswith('__description__'):
            delim = '"' if '"' in line else "'"
            _metadata['description'] = line.split(delim)[1]
    return _metadata


def parse_requirements(filename):
    """
    There is a parse_requirements function in pip but it keeps changing import path
    Let's build a simple one
    """
    try:
        with open(filename, 'r') as requirements_txt:
            install_requires = [
                str(requirement)
                for requirement
                in pkg_resources.parse_requirements(requirements_txt)
            ]
        return install_requires
    except OSError:
        print('WARNING: No requirements.txt file found as "{}". Please check path or create an empty one'
              .format(filename))


def get_long_description(filename):
    with open(filename, 'r', encoding='utf-8') as readme_file:
        _long_description = readme_file.read()
    return _long_description


#  ######### ACTUAL SCRIPT ENTRY POINT

NAMESPACE_PACKAGE_NAME = 'ofunctions'
namespace_package_path = os.path.abspath(NAMESPACE_PACKAGE_NAME)
namespace_package_file = os.path.join(namespace_package_path, '__init__.py')
metadata = get_metadata(namespace_package_file)
requirements = parse_requirements(os.path.join(namespace_package_path, 'requirements.txt'))

# Generic namespace package
setuptools.setup(
    name=NAMESPACE_PACKAGE_NAME,
    namespace_packages=[NAMESPACE_PACKAGE_NAME],
    packages=setuptools.find_namespace_packages(include=['ofunctions.*']),
    version=metadata['version'],
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: System",
        "Topic :: System :: Operating System",
        "Topic :: System :: Shells",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: BSD :: NetBSD",
        "Operating System :: POSIX :: BSD :: OpenBSD",
        "Operating System :: Microsoft",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: BSD License",
    ],
    description=metadata['description'],
    author='NetInvent - Orsiris de Jong',
    author_email='contact@netinvent.fr',
    url='https://github.com/netinvent/ofunctions',
    keywords=['network', 'bisection', 'logging'],
    long_description=get_long_description('README.md'),
    long_description_content_type="text/markdown",
    python_requires='>=3.5',
    # namespace packages don't work well with zipped eggs
    # ref https://packaging.python.org/guides/packaging-namespace-packages/
    zip_safe=False
)

for package in setuptools.find_namespace_packages(include=['ofunctions.*']):
    package_path = os.path.abspath(package.replace('.', os.sep))
    package_file = os.path.join(package_path, '__init__.py')
    metadata = get_metadata(package_file)
    requirements = parse_requirements(os.path.join(package_path, 'requirements.txt'))
    print(package_path)
    print(package_file)
    print(metadata)
    print(requirements)

    setuptools.setup(
        name=package,
        namespace_packages=[NAMESPACE_PACKAGE_NAME],
        packages=[package],
        package_data={package: ['__init__.py']},
        version=metadata['version'],
        install_requires=requirements,
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "Topic :: Software Development",
            "Topic :: System",
            "Topic :: System :: Operating System",
            "Topic :: System :: Shells",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Operating System :: POSIX :: Linux",
            "Operating System :: POSIX :: BSD :: FreeBSD",
            "Operating System :: POSIX :: BSD :: NetBSD",
            "Operating System :: POSIX :: BSD :: OpenBSD",
            "Operating System :: Microsoft",
            "Operating System :: Microsoft :: Windows",
            "License :: OSI Approved :: BSD License",
        ],
        description=metadata['description'],
        author='NetInvent - Orsiris de Jong',
        author_email='contact@netinvent.fr',
        url='https://github.com/netinvent/ofunctions',
        keywords=['network', 'bisection', 'logging'],
        long_description=get_long_description('README.md'),
        long_description_content_type="text/markdown",
        python_requires='>=3.5',
        # namespace packages don't work well with zipped eggs
        # ref https://packaging.python.org/guides/packaging-namespace-packages/
        zip_safe=False
    )
