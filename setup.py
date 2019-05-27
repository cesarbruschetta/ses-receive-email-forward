#!/usr/bin/env python3
import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md")) as f:
    README = f.read()

requires = ["boto3"]

tests_require = [
    "pytest",  # includes virtualenv
    "moto",
    "pytest-cov",
    "coverage==4.5.2",
    "nose==1.3.7",
]

setuptools.setup(
    name="forward-recieved-email",
    version="1.0",
    author="Cesar Augusto",
    author_email="cesarabruschetta@gmail.com",
    description="AWS SES Receiver e-mail forward e-mail other e-mail account",
    long_description=README,
    long_description_content_type="text/markdown",
    license="2-clause BSD",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
    extras_require={"testing": tests_require},
    install_requires=requires,
    python_requires=">=3.6",
    test_suite="tests",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
