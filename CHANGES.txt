.. -*- rst -*-

PyPFOP Changelog
================

0.3 [unreleased]
----------------

Changed
^^^^^^^

 - Split the functionality of ``pypfop.Document`` into a `builder` and `generator`
   steps in two separated modules: ``document_generator`` and ``builder``.

 - Rename the ``pypfop.Document`` class to ``pypfop.DocumentGenerator``,
   hopefully will better denote the intentions of the class.

 - Move the ``pypfop.makotemplates`` module to ``pypfop.templates.mako``,
   this will facilitate the extension of the template languages.

 - Rename the ``TemplateFactory`` class of the mako templates to ``Factory``
   inside the module ``pypfop.templates.mako``.

 - Upgrade the examples with the new API.

Added
^^^^^

 - Support for the FOPs generator fops_ with HTTP basic auth.

 - New base classes for the templates ``pypfop.templates.Template`` and
   ``pypfop.templates.Factory``. Basically, abstract classes.

 - New base skeletons to cover the base page for the paper sizes:
   `US Letter` and `A4` with  `landscape` and `portrait` orientations.

 - New base exceptions with no particular functionality than
   to indicate that they are related to the document generation
   of PyPFOP.

0.2 [2013-02-22]
----------------

Added
^^^^^
 - Support for python 2.


0.1.1 (2013-01-29)
------------------

Changed
^^^^^^^
 - Remove specify versions of the dependencies.

Fixed
^^^^^

 - Improve debug messages, configure the local logger and not the root logger.
 - Remove duplicate __template__ parameter in Document class.

Added
^^^^^

 - Allow the mako lookup_dirs to be just one string instead of a list.


.. _fops: https://github.com/cyraxjoe/fops
