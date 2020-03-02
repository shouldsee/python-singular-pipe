import inspect
# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from collections import namedtuple
import subprocess
from six import string_types

import functools
from singular_pipe.types import InputFile,OutputFile,File,TempFile, Path
from singular_pipe.types import Prefix,InputPrefix,OutputPrefix
from singular_pipe.types import job_result, PicklableNamedTuple, AttrDict
import singular_pipe.types 


def list_flatten(lst, strict=0, out=None, ):
	_this = list_flatten
	if out is None:
		out = []
	assert isinstance(lst, (tuple, list)),(type(lst), lst)
	for v in lst:
		if 0:
			pass
		elif isinstance(v,dict):
			v = v.items()
			_this(v, strict, out )
		elif isinstance(v,(list,tuple)):
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
		# @functools.wraps(func)
		# def gunc(*a,**kw):
		# 	return  func(func,*a,**kw)
		gunc = func
		try:
			res = inspect.getargspec(func)
		except Exception as e:
			import pdb;pdb.set_trace()
			raise e
		res = inspect.getargspec(func)
		args = res.args or []
		defaults = res.defaults or []
		assert args[0]  == 'self',(func, args)
		assert args[1]  == 'prefix',(func, args)
		assert args[-1] == '_output',(func, args)
		_output = defaults[-1]
		if  len(args) - len(defaults) > 2:
			 raise singular_pipe.types.TooFewDefaultsError(
			 	"Must specify a type for all of {args} for {func.__code__} (except first 2)".format(**locals()))
		defaults = ( singular_pipe.types.Default,OutputPrefix)[: len(args) -len(defaults)]+ defaults

		# if len(args)!=len(defaults):
		# 	 raise singular_pipe.types.TooFewDefaultsError(
		# 	 	"Must specify a type for all of {args} for {func.__code__}".format(**locals()))

		gunc._input_names = args[1:] ### in case (self=None,) and not (self,)
		gunc._input_types = defaults[1:]
		gunc._origin_code = getattr(func, '_origin_code', func.__code__)
		gunc._singular_pipe = True

		if 1:
			cls = gunc._output_type = func._output_type = PicklableNamedTuple('_output_type', _output)
			# cls = gunc._output_type = func._output_type = PicklableNamedTuple('_output_type', _output)
			cls._typed_fields = _output
			cls.__module__ = func.__module__
			cls.__qualname__ = "%s._output_type"%func.__name__
			# cls.__name__ = "%s._output"%func.__name__
		# gunc.__defaults__ = func.__defaults__
		return gunc

	def get_output_files( self, prefix, _output_typed_fields):
		'''
		Assuming all output_files are Prefix because types arent checked
		'''
		tups = []
		for s in _output_typed_fields:
			# print('[get-output]',s,type(s))
			# import pdb; pdb.set_trace();
			if not isinstance(s,(Prefix,File)):
				### Assuming type is Prefix  if unspecified
				assert isinstance(s,str),(type(s),s)
				typ = Prefix
			else:
				typ = type(s)
			s = "{prefix}.{self.__name__}.{suffix}".format(suffix = s, **locals())
			s = typ(str(s))
			assert not isinstance(s, (InputFile,InputPrefix)),('Must be Ouputxxx not Input...,%r'%s)
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



# if 1:
# 	def shell_cmd(cmd):
# 		pass

############### tests #############

def test_func_name():
	func_name1 = get_func_name(frame_default(None))
	func_name2 = get_func_name(None)
	print('[func_name]%s'%func_name1)
	print('[func_name]%s'%func_name2)
	return 




