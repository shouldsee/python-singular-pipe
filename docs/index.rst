.. singular_pipe documentation master file, created by
   sphinx-quickstart on Mon Mar  9 23:15:33 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to singular_pipe's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. * :ref:`my-reference_label`

.. _my-reference-label:

:mod:`singular_pipe._types` Internal types for detecting file and package 
changes 
-------------------------------------------------------------------------

.. automodule:: singular_pipe._types
    :show-inheritance:
    :members: Flow, FlowFunction, Node, NodeFunction,    Depend, PrefixedNode, File, Prefix,    
    LoggedShellCommand, LoggedSingularityCommand, Caller,FakeCode
    :undoc-members:
    :synopsis: Internal types for detecting file and package 
changes 


:mod:`singular_pipe.types` Entry point for all public callables 
---------------------------------------------------------------
.. automodule:: singular_pipe.types
    :show-inheritance:
    :members:
    :undoc-members:
    :synopsis: Entry point for all public callables


:mod:`singular_pipe.shell`
-------------------------
.. automodule:: singular_pipe.shell



:mod:`singular_pipe._types` --- Internal types to record system status
=====================================================================

.. .. autofunction:: io.open

.. .. automodule:: `singular_pipe`
..    :members:

.. :mod:`singular_pipe.types` --- Internal types to record system status
.. =====================================================================

.. .. module:: singular_pipe.types
..    :synopsis:  Internal types to record system status

.. .. function:: LoggedShellCommand(cmd_list[, output_handle[, strict]])
..    Executes a Shell command and save output to a file

.. .. class:: Caller()