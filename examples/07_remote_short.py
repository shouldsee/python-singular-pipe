'''
Since scripts are small, they can be uploaded to remote quickly
without pain
'''
from spiper.types import Node,Flow
from spiper.types import RemotePythonObject as RPO

package_path = 'spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/d457426'
@Flow
def simple_flow(
	self,prefix,
	_main= RPO(package_path, None, 'run_and_backup'),
	_output=[]
 ):

	func = _main.loaded()
	self.runner( func,  prefix, 1, 20, prefix+'_backup')	
	
	return self

if __name__ == '__main__':
	from path import Path
	from spiper.runner import get_changed_files,get_all_files,cache_run
	from pprint import pprint
	
	prefix = Path('/tmp/test_import/root')
	prefix.dirname().rmtree_p()

	fs = get_changed_files( simple_flow, prefix)
	pprint(fs)

	cache_run( simple_flow, prefix)

	fs = get_changed_files( simple_flow, prefix)
	pprint(fs)