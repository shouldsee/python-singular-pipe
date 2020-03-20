import argparse
import sys
from spiper.runner import cache_run,get_all_files,get_changed_files, force_run, mock_run
from spiper.types import RemotePythonObject as RPO
import spiper
from pprint import pprint

from pygments import highlight 
from pygments.lexers import get_lexer_by_name 
from pygments.formatters import HtmlFormatter 
from pygments.formatters import TerminalTrueColorFormatter,Terminal256Formatter,TerminalFormatter 
def highlight_python_code(code):
	lexer = get_lexer_by_name("python", stripall=True) 
	# formatter = HtmlFormatter(linenos=True, cssclass="source") 
	formatter = Terminal256Formatter()
	result = highlight(code, lexer, formatter) 
	return result
def _help(e=None):
	print('Version:spiper-%s'%spiper.VERSION)
	print(main.__doc__)
	if e is not None:
		raise e 
	return 0
	# sys.exit()

indent=4
_plain=[0]
def color_header(s):
	if not _plain[0]:
		return bcolors.HEADER+"{!s:<14}".format(s)+'\033[39m'
	else:
		return s

def node_dump(node,_write,ic):
	import io
	import textwrap
	def _writeline(s):
		_write( s +'\n')
	if node is None:
		_writeline(' '*indent*(ic)+color_header('node:')+ '\n'+' '*indent*(ic+1) + 'null')
	else:
		_writeline(' '*indent*(ic)+color_header('node:'))
		# to_dict = node.load_ident_file_key('to_dict')
		_writeline(textwrap.indent(color_header('prefix_named:')+ '\n'+' '*indent + node.prefix_named,' '*indent*(ic+1)))
		_writeline(textwrap.indent(color_header('job_type:')    + '\n'+' '*indent + node.job_type.__name__,' '*indent*(ic+1)))
		# _writeline(textwrap.indent(color_header('job_type:') + node.job_type.__name__,' '*indent*2))
		 # node.job_type.__name__,' '*indent*2))

		if node.is_fake:
			d = node.load_ident_file_key(None)
			assert d['version'] >= '0.1.2','Not supported for Caller with %s'%d['version']
			d = d['to_dict']
			d['will_change'] = 'NA when viewing a node image'
		else:
			d = node.to_dict()
			if node.is_node:
				d['will_change'] = str(not node.use_cache)
			else:
				d['will_change'] = 'True, FlowFunction will always be executed'
			# d['']

		# pprint(d)
		slines = d.pop('sourcelines')
		_writeline(textwrap.indent(color_header('will_change:')    + '\n'+' '*indent + d.pop('will_change'),' '*indent*(ic+1)))
		_writeline(textwrap.indent(color_header('dotname:')    + '\n'+' '*indent + d.pop('dotname'),' '*indent*(ic+1)))
		_writeline(textwrap.indent(color_header('sourcefile:') + '\n'+' '*indent + d.pop('sourcefile'),' '*indent*(ic+1)))

		_writeline(textwrap.indent(color_header('info_dict:'),' '*indent*(ic+1)))
		s = io.StringIO()
		pprint(d,s);s.seek(0)
		_writeline(textwrap.indent(s.read().rstrip(),' '*indent*(ic+2)))

		_writeline(textwrap.indent(color_header('sourcecode:'),' '*indent*(ic+1)))
		# _writeline('    '*2+'source_colored:')
		if _plain[0]:
			_writeline(textwrap.indent(('\n'.join(slines)),' '*indent*(ic+2)))
		else:
			_writeline(textwrap.indent(highlight_python_code('\n'.join(slines)),' '*indent*(ic+2)))

# _plain = [0]
def print_deps(fs):
	if _plain[0]:
		for f in fs:
			print(f)
	else:
		import json
		pprint(fs or '[No files governed by this workflow]')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main(args=None):
	__doc__ =r'''
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

		caller_show_deps     print all dependencies governed by workflow (legacy: get_all_deps)
			--plain          print a newline-separated list instead of pprint
			--which_flow     printing which subflow/node requries this dependency

		caller_show_log      print details of a call, including `arg_tuples,sourcecode,sourcefile`
			--plain

		file_show_deps       print dependencies of parent caller for a file
			--plain
			--which_flow
			
		file_show_log        print details of parent caller
			--plain

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
		callback = None
		if '--plain' in args:
			args.remove('--plain')
			plain = 1
		_plain[0] = plain

		flat = 0
		if '--flat' in args:
			args.remove('--flat')
			flat = 1

		if '--help' in args:
			return _help()
		if '--version' in args or '-V' in args:
			print('spiper-%s'%spiper.VERSION)
			return 0
		verbose = 0
		if '-v' in args:
			args.remove('-v')
			verbose = 1
		indent=4
		def color_header(s):
			return bcolors.HEADER+"{!s:<14}".format(s)+'\033[39m'

		file_cmds = ['file_show_log','file_upstream','file_show_deps']
		if args[0] in file_cmds:
			files = args[1:]
			if args[0]=='file_show_log':
				def _func(files=files, _write=lambda x:print(x,end='')):
					from spiper.graph import file_to_node,File
					import spiper
					import io
					for f in files:
						f = File(f).realpath()
						node = file_to_node(f	,0,spiper.rcParams['dir_layout'])
						def _write(s): print(s,end='')
						_write(color_header('file:')+'\n')
						_write(' '*indent*1+color_header('name:') )
						_write('\n'+' '*indent *2+ '%s\n'%f)
						node_dump(node, _write, 1)
			elif args[0] == 'file_show_deps':
				from spiper.runner import get_all_deps,file_to_node,File
				which_flow = 0
				if '--which_flow' in args:
					args.remove('--which_flow')
					which_flow = 1
				# def runner(*a,**kw):
				def _func(files=files):
					for f in files:
						print(f)
						node = file_to_node(File(f), 0, spiper.rcParams['dir_layout'])
						if not node:
							print('null')
						else:
							deps = node.get_all_deps(which_flow=which_flow)
							print_deps(deps)
		else:
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
			# elif args[0] == 'get_all_deps':
			# elif args[0] == 'node_show_deps':
			elif args[0] in ['get_all_deps', 'caller_show_deps']:
				from spiper.runner import get_all_deps
				which_flow = 0
				if '--which_flow' in args:
					args.remove('--which_flow')
					which_flow = 1
				def runner(*a,**kw):
					fs = get_all_deps(*a,which_flow=which_flow,**kw)
					print_deps(fs)

			elif args[0] == 'get_changed_files':
				def runner(*a,**kw):
					fs = get_changed_files(*a,**kw)
					if plain:
						for f in fs:
							print(f)
					else:
						pprint(fs or '[No files changed by this workflow]')
			elif args[0] == 'node_show_log':
				def runner(*a,**kw):
					return cache_run(*a,**kw,check_only=2)
				def callback(node):node_dump(node, sys.stdout.write, 0)
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
			def _func(
				# obj=obj,
				package=package,
				workflow_arguments=workflow_arguments,
				workflow_entrypoint=workflow_entrypoint,
				verbose=verbose,
				callback=callback,
				runner=runner,
				):
				obj = RPO(package, workflow_entrypoint)
				res = runner(obj.loaded(), *workflow_arguments,verbose=verbose)
				callback(res) if callback is not None else None
				return 0
	except Exception as e:
		return _help(e)
	retcode = _func() or 0
	return retcode

'''
PACKAGE=pipeline_rnaseq_hisat2_stringtie@file://$PWD
BIN="python3 -m spiper"
time $BIN file_log      _temp_build/*  | less  -R
time $BIN node_log $PACKAGE TOPLEVEL:test_job _temp_build/root | less -R

'''