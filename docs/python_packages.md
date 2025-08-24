# Python Packages 101

This project leverage Python packages to organize and structure the codebase. This document provides an overview of Python packages, their structure, and how to use them effectively.

## What is a Python Package?

A Python package is a way of organizing related Python modules into a single directory hierarchy. It allows for better organization and modularization of code, making it easier to manage and reuse.
A package can contain sub-packages, modules, and other resources like data files or documentation.

## `__init__.py`
The `__init__.py` file is a special file that indicates to Python that the directory should be treated as a package. It can be empty, or it can contain initialization code for the package. This file is executed when the package is imported, allowing you to set up any necessary state or configuration.

## `__main__.py`
The `__main__.py` file is a special file that allows a package to be run as a script. When you run a package using the `python -m package_name` command, Python will look for this file and execute it. This is useful for providing a command-line interface to your package.
It can also be used to define the main entry point for the package, allowing you to run the package directly without needing to specify a specific module.

## `pyproject.toml`
The `pyproject.toml` file is a configuration file for Python projects. It is used to define the build system requirements and metadata for the package.
This file is part of the [PEP 621](https://peps.python.org/pep-0621/) specification.


## How to use a Python Package

To use a Python package, you typically need to install it first. This can be done using the `pip` command in the terminal or command prompt. For example, to install a package named `example_package`, you would run:

```bash
pip install example_package
```
Once the package is installed, you can import it into your Python code using the `import` statement. For example:

```python
import example_package
from example_package import some_module
```
You can then use the functions, classes, and variables defined in the package as needed. For example:

```python
result = example_package.some_function()
print(result)
```
You can also use the `as` keyword to give the package or module a different name in your code:

```python
import example_package as ep
result = ep.some_function()
print(result)
```