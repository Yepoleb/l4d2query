#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="l4d2query",
    version="1.0.0",
    author="Gabriel Huber",
    author_email="mail@gabrielhuber.at",
    description="Query L4D2 server details",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yepoleb/l4d2query",
    packages=["l4d2query"],
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],
    python_requires=">=3.7"
)
