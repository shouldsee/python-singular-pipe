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
  * singularity >= 3.5.3 to use :obj:`spiper.shell.LoggedSingularityCommand`. ::

  	sudo apt-get update; 
  	curl -sL https://raw.githubusercontent.com/shouldsee/spiper/be4246b/scripts/install_singular.sh \
  	  | bash -s $HOME/.local    
   
  * `graphviz dot executable <https://www.graphviz.org/download/>`_  to use :obj:`spiper.graph.plot_simple_graph`

Installation
==============================

Install with pip
------------------------------

Find the version you want to install. For example, to install version |release|, use

.. code-block:: bash

	pip3 install spiper@https://github.com/shouldsee/spiper/tarball/|release| --user
