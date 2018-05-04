========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-herokuadmintools/badge/?style=flat
    :target: https://readthedocs.org/projects/python-herokuadmintools
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/hwine/python-herokuadmintools.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/hwine/python-herokuadmintools

.. |coveralls| image:: https://coveralls.io/repos/hwine/python-herokuadmintools/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/hwine/python-herokuadmintools

.. |codecov| image:: https://codecov.io/github/hwine/python-herokuadmintools/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/hwine/python-herokuadmintools

.. |version| image:: https://img.shields.io/pypi/v/herokuadmintools.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/herokuadmintools

.. |commits-since| image:: https://img.shields.io/github/commits-since/hwine/python-herokuadmintools/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/hwine/python-herokuadmintools/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/herokuadmintools.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/herokuadmintools

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/herokuadmintools.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/herokuadmintools

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/herokuadmintools.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/herokuadmintools


.. end-badges

Package to support both cli & pytest-services usage

* Free software: Apache Software License 2.0

Installation
============

::

    pip install herokuadmintools

Documentation
=============

https://python-herokuadmintools.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
