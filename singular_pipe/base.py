import inspect
# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from collections import namedtuple
import subprocess
from six import string_types

import functools
from singular_pipe.types import InputFile,OutputFile,File,TempFile, Path
from singular_pipe.types import Prefix,InputPrefix,OutputPrefix
from singular_pipe.types import job_result
import singular_pipe.types 

def list_flatten(lst, strict=0, out=None, ):
	_this = list_flatten
	if out is None:
		out = []
	for v in lst:
		if isinstance(v,(list,tuple)):
			_this(v, strict, out)
		else:
			if strict:
				assert isinstance(v,string_types),(type(v),v)
			out.append(v)
	return out
def list_flatten_strict(lst):
	return list_flatten(lst,strict=1)

def rstrip(s,suffix):
	if s.endswith(suffix):
		s = s[:-len(suffix)]
	return s


# import decorator
if 1:
	def job_from_func(func):
		# d = get_func_default_dict(func)
		@functools.wraps(func)
		def gunc(*a,**kw):
			return  func(func,*a,**kw)

		res = inspect.getargspec(func)
		args = res.args or []
		defaults = res.defaults or []
		assert args[0]  == 'self',(func, args)
		assert args[1]  == 'prefix',(func, args)
		assert args[-1] == '_output',(func, args)
		_output = defaults[-1]
		# if len(args)
		if len(args)!=len(defaults):
			 raise singular_pipe.types.TooFewDefaultsError(
			 	"Must specify a type for all of {args} for {func.__code__}".format(**locals()))

		gunc._input_names = args[1:] ### in case (self=None,) and not (self,)
		gunc._input_types = defaults[1:]
		gunc._origin_code = getattr(func, '_origin_code', func.__code__)

		if 1:
			cls = gunc._output_type = func._output_type = namedtuple('_output_type', _output)
			cls.__module__ = func.__module__
			cls.__qualname__ = "%s._output_type"%func.__name__
			# cls.__name__ = "%s._output"%func.__name__
		# gunc.__defaults__ = func.__defaults__
		return gunc

	def get_output_files( self, prefix, _output):
		'''
		Assuming all output_files are Prefix because types arent checked
		'''
		tups = []
		for suffix in _output:
			s = "{prefix}.{self.__name__}.{suffix}".format(**locals())
			s = singular_pipe.types.Prefix(s)
			tups.append(s)
		tups = self._output_type(*tups)
		return tups

	def get_func_name(frame=None):
		if frame is None:
			frame = frame_default(None).f_back
		else:
			frame = frame_default(frame)
		return frame.f_code.co_name

	def frame_default(frame):
		if frame is None:
			frame = inspect.currentframe().f_back
		return frame
	def get_func_default_dict(func):
		a = inspect.getargspec(func)
		args = a.args or []
		defaults = a.defaults or []
		return dict(zip( 
			args[-len(defaults ):], 
			defaults))


import json
import warnings

if 1:
	def singularity_run( cmd, image, extra_files = None, debug =0):	
		'''
		return a tuple (executed command, command_stdout)
			cmd: a list of str-like objects that gets concatenated into a shell command
			image: a singularity image url
			extra_files: to-be-deprecated
			debug: print dbg info
		'''
		if extra_files is None:
			extra_files  = []
		cmd = list_flatten_strict(cmd)

		#### potential redundant
		#### all output path derives from Prefix hence only Prefix needs to be realpath
		#### for input path, realisation better be done at job calling
		out = []
		for x in cmd:
			if isinstance(x,Path):
				x = x.realpath()
			if x.startswith('/tmp'):
				warnings.warn('[singularity_run] with /tmp is unstable')
			out.append(x)
		cmd = out

		# debug = 1
		if debug: print(json.dumps(list(map(repr,cmd)),indent=4,))

		FS,modes = make_files_for(cmd)
		if debug: print(json.dumps(list(map(repr,FS)),indent=4,))

		bfs = [':'.join([f,f,m]) for f,m in zip(FS,modes)]
		# bfs = bind_files( FS + extra_files) 
		if debug: print(json.dumps(list(map(repr,bfs)),indent=4,))

		cmd_curr = [
		# '\n',
		'singularity','exec',
		'--contain',
		['--bind',','.join(bfs)] if len(bfs) else [],
		# [-1],'--bind','/tmp:/tmp',
			image,
			'bash',
			'<<EOF\n',
			cmd,
			'\nEOF',
		# '\n',
		]
		cmd_curr = list_flatten_strict(cmd_curr)
		res = subprocess.check_output(' '.join(cmd_curr),shell=1)
		return (cmd_curr, res)

	def make_files_for(cmd):
		FS = []
		modes = []
		for F in cmd:
			if isinstance(F, (File,Prefix)):
				F = F.realpath()
				if isinstance(F, InputPrefix):
					#### if is prefix, mount the directory
					res = F.fileglob('*',1) 
					FS += res
					modes += ['ro']*len(res)
				elif isinstance(F, Prefix):
					#### if is not inputPrefix, mount the directory
					F.dirname().makedirs_p()
					FS.append( File( F.dirname() ) )
					mode = 'rw'
					modes+=[mode]
				elif isinstance(F, InputFile):
					#### if is inputFile, dont touch
					assert F.isfile(),(F,cmd)
					FS.append( F )
					modes += ['ro']					
				elif isinstance(F,File):
					#### if not inputfile, touch to makesure					
					F.touch() if not F.isfile() else None
					FS.append( F )
					modes += ['rw']
					# mode = 'rw'
				else:
					assert 0,(type(F),F)
				# FS.append(F)	
		assert len(FS) == len(modes)
		return FS,modes

	def bind_files(files):
		assert 0,'DEPRECATED'
		files = list_flatten(files)
		lst = []
		for F in files:
			#### bind the whole directory for a prefix
			if isinstance(F,Prefix):
				assert 0,(F,'run make_files_for() first', files)
			elif isinstance(F, InputFile):
				mode = 'ro'
			elif isinstance(F,File):
				mode = 'rw'
			else:
				assert 0,(F,"type %s unknown"%type(F),files,)
			F = F.realpath()
			bind_str = "%s:%s:%s"%( F, F, mode)
			lst.append( bind_str )
		return lst		
############### tests #############

def test_func_name():
	func_name1 = get_func_name(frame_default(None))
	func_name2 = get_func_name(None)
	print('[func_name]%s'%func_name1)
	print('[func_name]%s'%func_name2)
	return 




