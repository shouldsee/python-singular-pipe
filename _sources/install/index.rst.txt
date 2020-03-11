.. _install-index:

******************************************************
Installation
******************************************************


Dependencies
====================================

This package is tested to be compatible with python3.5 and python3.7. Please create a github PR if you
want another version to be added. Python2 is not supported.

Essential
--------------------------
  * Python 3.5 / Python 3.7
  * pip >= 18.1

Optional
---------------------------
  * singularity >= 3.5.3 to use :obj:`spiper.shell.LoggedSingularityCommand`.  Convenience script ``curl -sL https://raw.githubusercontent.com/shouldsee/spiper/7ef9673/scripts/install_singular.sh | bash -s /opt/singularity``    
  * `graphviz dot executable <https://www.graphviz.org/download/>`_  to use :obj:`spiper.graph.plot_simple_graph`

Installation
==============================

Install with pip
------------------------------

Find the version you want to install. For example, to install version 0.0.3, use

.. code-block:: bash

	pip3 install spiper@https://github.com/shouldsee/spiper/tarball/0.0.3 --user
