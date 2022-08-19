from os import getenv

from setuptools import setup, find_packages
from os.path import abspath, dirname, join

README_MD = open(join(dirname(abspath(__file__)), "README.md")).read()

version = getenv("GITHUB_REF", "")
version = version[version.find("v") + 1:]
if len(version) != 5:
    raise Exception("Version is not in the right format")

setup(
    name="lazy_runtime_typechecker",
    version=version,
    packages=find_packages(),
    description="Simple runtime typechecker",
    long_description=README_MD,
    long_description_content_type="text/markdown",
    url="https://github.com/lzMeMod/runtime-typechecker",
    author_name="lzMeMod",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="typing, runtime, typechecker",
)
