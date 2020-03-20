import argparse
import sys
from spiper.runner import cache_run,get_all_files,get_changed_files, force_run, mock_run
from spiper.types import RemotePythonObject as RPO
import spiper
def _help(e=None):
	print('Version:spiper-%s'%spiper.VERSION)
	print(main.__doc__)
	if e is not None:
		raise e 
	return 0
	# sys.exit()

from pprint import pprint
def main(args=None):
	r'''
Usage

	``spiper <subcommand> <package> <workflow_entrypoint> <workflow_arguments>``

Example::

	spiper run \
	  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
	  spiper_mock_flow:run_and_backup \
	  /tmp/test_remote/root 1 2 /tmp/test_remote/root.backup

Arguments:
	<subcommand>:
		run                  execute the workflow
		get_all_files        print all files governed by workflow
			--plain          print a newline-separated list instead of pprint
		get_changed_files    print all files changed by workflow
			--plain          print a newline-separated list instead of pprint
		get_all_deps         print all dependencies governed by workflow
			--plain          print a newline-separated list instead of pprint
			--which_flow     printing which subflow/node requries this dependency
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

		plain = 0
		if '--plain' in args:
			args.remove('--plain')
			plain = 1

		if '--help' in args:
			return _help()
		if '--version' in args or '-V' in args:
			print('spiper-%s'%spiper.VERSION)
			return 0
		verbose = 0
		if '-v' in args:
			args.remove('-v')
			verbose = 1

		if args[0]=='run':
			runner = cache_run		
			if '--force' in args:
				args.remove('--force')
				runner = force_run
			if '--mock' in args:
				args.remove('--mock')
				runner = mock_run

		elif args[0] == 'get_all_files':
			def runner(*a,**kw):
				fs = get_all_files(*a,**kw)
				if plain:
					for f in fs:
						print(f)
				else:
					pprint(fs or '[No files governed by this workflow]')
		elif args[0] == 'get_all_deps':
			from spiper.runner import get_all_deps
			which_flow = 0
			if '--which_flow' in args:
				args.remove('--which_flow')
				which_flow = 1
			def runner(*a,**kw):
				fs = get_all_deps(*a,which_flow=which_flow,**kw)
				if plain:
					for f in fs:
						print(f)
				else:
					# pp
					# [print(f) for f in fs or ['[No dependcies detected]']]
					# pprint(fs or '[No dependcies detected]',indent=2)
					import json
					# import collections
					# if isinstance(fs,dict):
					# 	fs = collections.OrderedDict([(repr(k),v) for k,v in fs.items()])
					# json.dump( fs, sys.stdout,default=repr,indent=2) if fs else print('[No files governed by this workflow]')
					pprint(fs or '[No files governed by this workflow]')

		elif args[0] == 'get_changed_files':
			def runner(*a,**kw):
				fs = get_changed_files(*a,**kw)
				if plain:
					for f in fs:
						print(f)
				else:
					pprint(fs or '[No files changed by this workflow]')
		else:
			return _help(Exception('Unknown args[0] %s'%args[0]))

		if '--comma' in args:
			comma = 1
			args.remove('--comma')
		else:
			comma = 0
		package = args[1]
		workflow_entrypoint = args[2]
		if not comma:
			workflow_arguments = args[3:]
		else:
			workflow_arguments = (args[3:4] or [''])[0].split(',')
	except Exception as e:
		return _help(e)

	obj = RPO(package, workflow_entrypoint)
	res = runner(obj.loaded(), *workflow_arguments,verbose=verbose)
	return 0
