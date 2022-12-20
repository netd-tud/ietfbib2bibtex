==============
ietfbib2bibtex
==============

This tool aims to convert the XML-based formats of the IETF (`bibxml`_ and `rfc-index`_) to
`bibtex`_ format.

Installation
============
TBD when GitHub is there

.. code:: bash

   pip install .

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
``ietfbib2bibtex`` directory in the corresponding user configuration [appdir] of your operating
system.

.. _`appdir`: https://pypi.org/project/appdirs/
.. _`bibtex`: http://bibtex.org
.. _`bibxml`: https://bib.ietf.org/
.. _`config.yaml.example`: ./config.yaml.example
.. _`Python`: https://docs.python.org
.. _`rfc-index`: https://www.rfc-editor.org/rfc-index.xml
