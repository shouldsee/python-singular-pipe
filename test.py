from spiper.test.base import debugTestRunner
import sys
import unittest2
import spiper.test.graph
import spiper.test.base
import spiper.test.mock

# import spiper.test.test_graph

# from spiper.test.base import BaseCase as all
if __name__ == '__main__':
	# print('[testing]%s'%__file__)
	if '--all' in sys.argv:
		from spiper.test.graph import Case as case1
		from spiper.test.base import BaseCase as case2
		from spiper.test.mock import Case as case3

		del sys.argv[sys.argv.index('--all')]
		
	if '--pdb' in sys.argv:
		del sys.argv[sys.argv.index('--pdb')]
		unittest2.main(testRunner=debugTestRunner())
	else:
		unittest2.main(testRunner=None)

