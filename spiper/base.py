import inspect
# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from collections import namedtuple
import subprocess
from six import string_types

import functools
from spiper._types import InputFile,OutputFile,File,TempFile, Path
from spiper._types import Prefix,InputPrefix,OutputPrefix
from spiper._types import job_result, PicklableNamedTuple, AttrDict
from spiper._types import list_flatten,list_flatten_strict
import spiper._types 



class ReservedKeyword(Exception):
	pass

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
		assert args[0]  == 'self',(func.__code__, args)
		assert args[1]  == 'prefix',(func.__code__, args)
		assert args[-1] == '_output',(func.__code__, args)
		_output = defaults[-1]
		if '_output' in _output:
			raise ReservedKeyword( "%r is a reserved keyword in object:%r" %('_output', _output) )
		# for i,v in eumerate(_output):
			# if isinstance(v, File):
			# 	v = OutputFile(v)
			# elif isinstance(v,Prefix):
			# 	v = Out
		if  len(args) - len(defaults) > 2:
			 raise spiper._types.TooFewDefaultsError(
			 	"Must specify a type for all of {args} for {func.__code__} (except first 2)".format(**locals()))
		# defaults = ( spiper._types.Default, OutputPrefix)[: len(args) -len(defaults)]+ defaults
		defaults = ( spiper._types.Default, File)[: len(args) -len(defaults)]+ defaults
		assert defaults[1]==File,'default for the second argument must be "File" !'
		# if len(args)!=len(defaults):
		# 	 raise spiper._types.TooFewDefaultsError(
		# 	 	"Must specify a type for all of {args} for {func.__code__}".format(**locals()))

		gunc._input_names = args[1:] ### in case (self=None,) and not (self,)
		gunc._input_types = defaults[1:]
		gunc._origin_code = getattr(func, '_origin_code', func.__code__)
		gunc._spiper = True

		if 1:
			cls = gunc._output_type = func._output_type = PicklableNamedTuple('_output_type', _output)
			# cls = gunc._output_type = func._output_type = PicklableNamedTuple('_output_type', _output)
			cls._typed_fields = _output
			cls.__module__ = func.__module__
			cls.__qualname__ = "%s._output_type"%func.__name__
			# cls.__name__ = "%s._output"%func.__name__
		# gunc.__defaults__ = func.__defaults__
		return gunc



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



############### tests #############

def test_func_name():
	func_name1 = get_func_name(frame_default(None))
	func_name2 = get_func_name(None)
	print('[func_name]%s'%func_name1)
	print('[func_name]%s'%func_name2)
	return 




