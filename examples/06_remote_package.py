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

from singular_pipe.types import Node,Flow
from singular_pipe.types import PythonModule, PythonFunction

# Github "tarball/master" often take minutes to update,
# use the commit hash to ensure integrity. 
package_path = 'singular_pipe_mock_flow@https://github.com/shouldsee/singular_pipe_mock_flow/tarball/d457426'
# package_path = 'singular_pipe_mock_flow@http://github.com/shouldsee/singular_pipe_mock_flow/tarball/master'
# package_path = 'singular_pipe_mock_flow@file:///home/user/repos/singular_pipe/d457426'

@Flow
def test_import(self,prefix,
 _remote_mod = PythonModule(package_path),
 # _remote_mod_v = PythonModule(package_path,  '==0.0.1'), 
 ### version should be contained in packge_path already. 
 ### hence version is not supported for this kind of dependency
 _remote_function = PythonFunction(package_path, 'run_and_backup'),
 # _remote_function_v = PythonFunction(package_path, '==0.0.1','run_and_backup'),
 _output=[]):
	_mod = _remote_mod.loaded()
	run_and_backup = _mod.run_and_backup
	run_and_backup = _remote_function.loaded()
	self.runner( run_and_backup, prefix, 1, 20, prefix+'_backup')
	return self

package_path = 'singular_pipe_mock_flow@https://github.com/shouldsee/singular_pipe_mock_flow/tarball/d457426'
@Flow
def simple_flow(self,prefix,
 _main= PythonFunction(package_path, 'run_and_backup'),
 _output=[]):
	self.runner(_main.loaded(),  prefix, 1, 20, prefix+'_backup')	
	return self



def main():
	import singular_pipe
	from path import Path
	from singular_pipe.runner import get_all_files, get_changed_files, cache_run
	from pprint import pprint
	# singular_pipe.rcParams['dir_layout'] = 'flat' 

	prefix = Path('/tmp/test_import/root')
	prefix.dirname().rmtree_p()

	fs = get_changed_files(test_import, prefix)
	pprint(fs)

	fs = get_all_files(test_import,prefix)
	pprint(fs)

	### run actual workflow
	cache_run(test_import,prefix)

	fs = get_changed_files(test_import, prefix)
	pprint(fs)
	assert fs == []

	get_changed_files(simple_flow, prefix)
	pprint(fs)
	assert fs == []

if __name__ == '__main__':
	main()