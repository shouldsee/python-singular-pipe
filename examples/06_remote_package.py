'''
Vanilla python modules present import statements at the beginning of its scripts
this prevents the specification of remote package though http:// and produces
maintainence problems. Here we propose an in-function import system that
install packages only during real-execution of NodeFunction(). This way,
package dependency and scripts could live in the same python file, but yet
be decoupled in the sense that only execution of a node invokes dependency installation. 

This in-function dependency is compatible with the old setup.py style dependency. The
only difference is that previous dependency is specified at the package-level whereas
this dep is at function-level.

The purpose of enabling a remote package specification is to 
centralise the storage of pipelines to cloud rather than to a local machine, which
would force the script creator to write the script in a local-independent way.
'''

from spiper.types import Node,Flow
from spiper.types import PythonPackage, RemotePythonObject,RPO

# Github "tarball/master" often take minutes to update,
# use the commit hash to ensure integrity. 
# package_path_with_hash = 'spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/d457426'
# package_path           = 'spiper_mock_flow@http://github.com/shouldsee/spiper_mock_flow/tarball/master'





##### showing many different ways of
@Flow
def test_import(self,prefix,
		_mod1 = RemotePythonObject('spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/d457426'),
			### import the top-level module of the package
		_remote_function= RemotePythonObject(
			'spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/d457426',
			None,  
			'run_and_backup'),
		 ### import a function from toplevel module
		_mod2 = RemotePythonObject(
			'luigi@https://github.com/spotify/luigi/tarball/2.8.12',
			'luigi',),
			### import a module with different name
		_mod2attr = RemotePythonObject(
			'luigi@https://github.com/spotify/luigi/tarball/2.8.12',
			'luigi.event', 
			'Event'),
			### import a function from a module
		_output=[]
	):
	_mod1 = _mod1.loaded()
	_mod2 = _mod2.loaded()
	_mod2attr.loaded()
	print('[IMPORTED]!!',_mod2attr.loaded())
	return self


def main():
	import spiper
	from path import Path
	from spiper.runner import get_all_files, get_changed_files, cache_run
	from pprint import pprint
	spiper.rcParams['dir_layout'] = 'flat' 

	prefix = Path('/tmp/test_import/root')
	prefix.dirname().rmtree_p()

	print('#### [Note] currently the package change is not recorded')
	fs = get_changed_files(test_import, prefix) 
	pprint(fs)
	fs = get_all_files(test_import,prefix)
	pprint(fs)
	cache_run(test_import,prefix)
	pprint(fs)

	print('#### [Note] Remote workflow should detect file changes')
	fs = get_changed_files(simple_flow, prefix)
	pprint(fs)
	assert fs != []

	print('### run actual workflow')
	cache_run(simple_flow,prefix)

	fs = get_changed_files(simple_flow, prefix)
	pprint(fs)
	assert fs == []

if __name__ == '__main__':
	main()