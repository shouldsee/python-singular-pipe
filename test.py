from singular_pipe.test.base import debugTestRunner
import sys
import unittest2
import singular_pipe.test.graph
import singular_pipe.test.base
# import singular_pipe.test.test_graph

# from singular_pipe.test.base import BaseCase as all
if __name__ == '__main__':
	print('[testing]%s'%__file__)
	if '--all' in sys.argv:
		del sys.argv[sys.argv.index('--all')]
		from singular_pipe.test.base import *
		from singular_pipe.test.graph import *
	if '--pdb' in sys.argv:
		del sys.argv[sys.argv.index('--pdb')]
		unittest2.main(testRunner=debugTestRunner())
	else:
		unittest2.main(testRunner=None)

