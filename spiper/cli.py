import argparse
import sys
from spiper.runner import cache_run,get_all_files,get_changed_files
from spiper.types import RemotePythonObject as RPO
def _help(e=None):
	print(main.__doc__)
	if e is not None:
		raise e 
	sys.exit()

def main(args=None):
	r'''
Usage:
	spiper <subcommand> <package> <workflow_entrypoint> <workflow_arguments>

Example:
	spiper run \
	  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
	  spiper_mock_flow:run_and_backup \
	  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup

Arguments:
	<subcommand>:
		run                  execute the workflow
		get_all_files        print all files governed by workflow
		get_changed_files    print all files changed by workflow
	<package>:
		a string compatible with pep-508
	<workflow_entrypoint>:
		a string  "<module>:<object_name>" where object is like a `spipe.types.Node()`
	<workflow_arguments>:
		a comma-separated list of arguments for the workflow

Options:
	--help: show this help

	'''
	try:
		if args is None:
			args = sys.argv[1:]
		if '--help' in args:
			_help()
		if args[0]=='run':
			runner = cache_run		
		elif args[0] == 'get_all_files':
			runner = get_all_files
		elif args[0] == 'get_changed_files':
			runner = get_changed_files
		else:
			_help()
		package = args[1]
		workflow_entrypoint = args[2]
		workflow_arguments = (args[3:4] or [''])[0]
		inputs = [] if not workflow_arguments else workflow_arguments.split(',')
	except Exception as e:
		_help(e)

	obj = RPO(package, workflow_entrypoint)
	res = runner(obj.loaded(), *inputs)
	return 0
