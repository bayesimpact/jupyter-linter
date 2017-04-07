"""Bayes Impact Jupyter Notebook Linter."""

import os
from pip.req import parse_requirements
import setuptools
import sys


install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]


if 'publish' in sys.argv:
    # Publish current version to Pypi.
    # TODO: Tag the repo with the new version number.
    os.system("python setup.py sdist upload")
    sys.exit()

setuptools.setup(
    name='bayes-jupyter-linter',
    description=(
        'A simple linter to enforce the rules of the Bayes Impact '
        'style guide https://goo.gl/lhK4JT.'),
    version='0.0.1',
    packages=['jupyter_linter'],
    author='Stephan Gabler',
    author_email='stephan@bayesimpact.org',
    url='https://github.com/bayesimpact/jupyter-linter',
    license='The MIT License (MIT)',
    keywords=['linter'],
    install_requires=reqs,
    entry_points={
        'console_scripts': ['bayes-jupyter-linter=jupyter_linter:main'],
    }
)
