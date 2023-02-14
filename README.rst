==============
ietfbib2bibtex
==============

.. image:: https://github.com/ilabrg/ietfbib2bibtex/actions/workflows/test.yml/badge.svg
  :target: https://github.com/ilabrg/ietfbib2bibtex/actions/workflows/test.yml

.. image:: https://codecov.io/gh/ilabrg/ietfbib2bibtex/branch/main/graph/badge.svg?token=UKAN36HVBT
  :target: https://codecov.io/gh/ilabrg/ietfbib2bibtex

This tool aims to convert the XML-based formats of the IETF (`bibxml`_ and `rfc-index`_) to
`bibtex`_ format.

Installation
============
You can install ietfbib2bibtex using the GitHub link:


.. code:: bash

   pip install git+https://github.com/ilabrg/ietfbib2bibtex/

Dependencies
------------
ietfbib2bibtex works on `Python`_ 3.7 or newer.

See requirements.txt for the packages required.

Usage
=====

First you need a configuration file in YAML format. See config.yaml.example for an example.

Then, you can run

.. code:: bash

   ietfbib2bibtex -c "<config-file>"

If you do not provide a configuration file with the ``-c`` argument, it is expected to be in the
``ietfbib2bibtex`` directory in the corresponding user configuration `platformdirs`_ of your
operating system.

.. _`bibtex`: http://bibtex.org
.. _`bibxml`: https://bib.ietf.org/
.. _`config.yaml.example`: ./config.yaml.example
.. _`platformdirs`: https://platformdirs.readthedocs.io
.. _`Python`: https://docs.python.org
.. _`rfc-index`: https://www.rfc-editor.org/rfc-index.xml
