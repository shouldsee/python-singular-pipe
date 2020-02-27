import inspect
# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from collections import namedtuple
import subprocess
from six import string_types

import functools
from singular_pipe.types import InputFile,OutputFile,File,TempFile, Prefix,Path



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
			a[0].dirname().makedirs_p()
			return  func(func,*a,**kw)
		res = inspect.getargspec(func)
		args = res.args or []
		defaults = res.defaults or []
		assert args[0]  == 'self',(func, args)
		assert args[-1] == '_output',(func, args)
		defaults,_output  = defaults[:-1],defaults[-1]
		args = args[:-1]
		gunc._input_names = args[-len(defaults):] ### in case (self=None,) and not (self,)
		gunc._input_types = defaults

		if 1:
			cls = gunc._output_type = func._output_type = namedtuple('_output_type', _output)
			cls.__module__ = func.__module__
			cls.__qualname__ = "%s._output_type"%func.__name__
			# cls.__name__ = "%s._output"%func.__name__
		# gunc.__defaults__ = func.__defaults__
		return gunc

	def get_output_files( self, prefix, _output):
		tups = []
		for suffix in _output:
			s = "{prefix}.{self.__name__}.{suffix}".format(**locals())
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

		FS = make_files_for(cmd)
		if debug: print(json.dumps(list(map(repr,cmd)),indent=4,))

		bfs = bind_files( FS + extra_files) 
		if debug: print(json.dumps(list(map(repr,bfs)),indent=4,))

		cmd_curr = [
		# '\n',
		'singularity','exec',
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
		for F in cmd:
			if isinstance(F, (File,Prefix)):
				F.dirname().makedirs_p()
				if not isinstance(F, InputFile):
					F.touch()
				FS.append(F)
		return FS

	def bind_files(files):
		files = list_flatten_strict(files)
		lst = []
		for F in files:
			F = F.realpath()
			F.dirname().makedirs_p()
			#### bind the whole directory for a prefix
			if isinstance(F,Prefix):
				F = F.dirname()
			if isinstance(F, InputFile):
				mode = 'ro'
			else:
				mode = 'rw'
			bind_str = "%s:%s:%s"%( F.realpath(), F.realpath(), mode)
			lst.append( bind_str )
		return lst		
############### tests #############

def test_func_name():
	func_name1 = get_func_name(frame_default(None))
	func_name2 = get_func_name(None)
	print('[func_name]%s'%func_name1)
	print('[func_name]%s'%func_name2)
	return 




