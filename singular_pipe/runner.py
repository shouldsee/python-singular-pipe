from singular_pipe.types import File,InputFile,OutputFile, Prefix
from singular_pipe.types import TooManyArgumentsError
import singular_pipe.types

from singular_pipe.base import get_output_files,get_func_name, list_flatten
import pickle
import os,sys
import json
from itertools import zip_longest
from collections import namedtuple
import inspect

def force_run(job, *args,**kw):
	'''
	Run a jobs regardless of whether it has a valid cache
	'''
	return cache_run(job,*args,force=True,**kw)
	_input = args
	res = job(*_input)
	return res
def cache_check(job, *args,**kw):
	'''
	Check whether there is a valid cache for this job
	'''
	return cache_run(job,*args,check_only=True,**kw)
def cache_check_changed(job,*args,**kw):
	return cache_run(job,*args,check_changed=True,**kw)

def cache_run_verbose(job,*args, **kw):
	return cache_run(job,*args,verbose=True,**kw)

# def ident_changed(ident, ident_file):
# 	ident_dump     = pickle.dumps(ident)
# 	ident_dump_old = open(ident_file,'rb').read() if file_not_empty(ident_file) else b''
# 	return ident_dump != ident_dump_old

# def ident_dump(ident, ident_file, comment=''):
# 	with open(ident_file,'wb') as f:
# 		pickle.dump( ident,  f )


def ident_load(ident_file,key ='ident'):	
	ident_dump_old = ''
	try:
		if file_not_empty(ident_file):
			ident_dump_old = str(json.loads(open(ident_file,'r').read())[key])
	except Exception as e:
		raise e
		print(e)
	return ident_dump_old
def ident_changed(ident, ident_file, key ='ident'):
	ident_dump = str(pickle.dumps(ident))
	ident_dump_old = ident_load( ident_file, key )
	return ident_dump != ident_dump_old

def ident_dump(ident, ident_file, comment=''):	
	with open(ident_file,'w') as f:
		json.dump(collections.OrderedDict([
			('comment',comment),
			('ident', str(pickle.dumps(ident)) )
			]),
		# .decode('utf8'))]),
		f,
		indent=2,
		)
		# pickle.dump( ident,  f )

def _raise(e):
	raise e

_Caller = namedtuple('_Caller',
	['job',
	'arg_tuples'])
def func_orig(func):
	while hasattr(func,'__wrapped__'):
		func = func.__wrapped__
	return func


import collections
# class Caller( _Caller):
class Caller(object):
	@classmethod
	def from_input(Caller, job, _input):
		_tmp  = []
		_null = namedtuple('_null',[])()
		_zip = lambda: zip_longest(job._input_names, job._input_types, _input,fillvalue=_null)
		_dump = lambda: json.dumps([repr(namedtuple('tuple','argname type input_value')(*x)) for x in _zip()],indent=0,default=repr)
		for n,t,v in _zip():
			if n[0]=='_':
				if v is not _null:
					raise TooManyArgumentsError('{dump}\nToo many arguments specified for {job._origin_code}\n argname started with _ should not have input_value \n'.format(
						dump=_dump(),**locals()))
			elif v is _null:
				raise singular_pipe.types.TooFewArgumentsError(
					'{dump}\nToo few arguments specified for {job._origin_code}\n argname started with _ should not have input_value \n'.format(
				dump=_dump(),**locals()))
			else:
				_tmp.append( (n, t(v)) )
		_caller = Caller( job, _tmp[:])
		return _caller

	def __init__(self, job,arg_tuples):
		self.job = job
		self.arg_tuples = arg_tuples
	@property
	def f(self):
		return func_orig(self.job)
	def to_ident(self):
		'''
		For pickle.dumps
		'''
		f = self.f
		### argument to jobs without prefix
		_job_args = list(zip(*self.arg_tuples[1:])) 
		_input = [
		(	f.__code__.co_code, 
			f.__code__.co_consts),
			_job_args,
		]		
		return _input
	def to_dict(self):
		'''
		For visualisation / json.dumps
		'''
		f = self.f
		res = collections.OrderedDict([
				('job', repr(f.__code__)),
				('dotname',"%s.%s"%(inspect.getmodule(f).__name__, f.__qualname__)),
				('arg_tuples', collections.OrderedDict([(k,repr(v).strip('"'"'")) for k,v in self.arg_tuples]) ),
				# ('co_code',f.__code__.co_code),
				# ('co_consts',f.__code__.co_consts),
				])
		return res		

	def __repr__(self):
		f = self.f
		return '%s.%s(%s)'%(
			self.__class__.__module__,
			self.__class__.__name__,
			json.dumps( self.to_dict(),
			indent=2,default=repr)
			)
	def __call__(self,):
		return self.job(*[x[1] for x in self.arg_tuples])


def cache_run(job, *args, check_only=False, check_changed=False, force=False,verbose=0):
	'''
	return: job_result
		Check whether a valid cache exists for a job receipe.
		Load cache as result if so, otherwise recalculate the job.

	##### we want to avoid re-calculating the output if they already exist and is intact
	##### this is done by storing an identity information on disk 
	##### this identity information is calculated from the outputted files
	##### which could be md5sum or timestamp		
	'''
	func_name = get_func_name()
	prefix = args[0]

	suf = 'json'
	input_ident_file  = '{prefix}.{job.__name__}.input_{suf}'.format(**locals())
	output_ident_file = '{prefix}.{job.__name__}.output_{suf}'.format(**locals())
	output_cache_file = '{prefix}.{job.__name__}.cache_pk'.format(**locals())

	###### the _input is changed if one of the func.co_code/func.co_consts/input_args changed
	###### the prefix is ignored in to_ident() because it would point to a different ident_file
	#####  Caller.from_input() would also cast types for inputs
	_input = args
	_caller = Caller.from_input(job, _input)
	_input  = [_caller.to_ident()]	
	# print(_dump()) if verbose>=2 else None
	print(repr(_caller)) if verbose >= 3 else None

	#### calculate output files
	### cast all files all as prefix
	### here we add cache_file as a constitutive output.
	_output = get_output_files( job, prefix, job._output_type._fields) + (OutputFile(output_cache_file),)
	# print('[out1]',_output)
	# _output = [Prefix(o) for o in _output] + [OutputFile(output_cache_file)]
	# print('[out2]',_output)
	# print('[out3]',get_identity(_output))

	_ddump = lambda *a:json.dumps(*a,indent=2,default=repr)
	# print(_ddump(list(map(repr,get_identity(_input)))))
	input_ident_changed  = ident_changed( get_identity( _input, ), input_ident_file)
	output_ident_changed = ident_changed( get_identity( _output, ), output_ident_file)		
	use_cache = not input_ident_changed and not output_ident_changed
	if check_only:
		return use_cache
	if check_changed:
		return (input_ident_changed, output_ident_changed)

	if verbose:
		print('[{func_name}]'.format(**locals()),
			json.dumps([
			('job_name',job.__name__),
			('input_ident_changed', int(input_ident_changed)),
			('output_ident_chanegd',int(output_ident_changed))]
				,separators='_=').replace('"','')
			)

	if check_only:
		return bool(use_cache)		

	if force:
		use_cache = False

	if use_cache:
		# indent
		# with open(
		# result = pickle.loads(bytes(ident_load( output_cache_file )))
		with open(output_cache_file,'rb') as f:
			result = pickle.load(f)

	else:
		result = _caller()
		with open(output_cache_file,'wb') as f: pickle.dump(result, f)
		# ident_dump( result, output_cache_file, )
		ident_dump( get_identity(_output), output_ident_file, comment = [(_output,get_identity(_output))] ) ### outputs are all
		ident_dump( get_identity(_input), input_ident_file, comment = _caller.to_dict())
	return result


def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
    if os.path.isfile(fname):
        return os.stat(fname)
    else:
        return _os_stat_result_null

def get_identity(lst, out = None,verbose=0):
	'''
	Append to file names with their mtime and st_size
	'''
	if out is None:
		out = []
	for ele in list_flatten(lst):
		if isinstance(ele, Prefix):
			res = ele.fileglob("*")
			print('[expanding]\n  %r\n  %r'%(ele,res)) if verbose else None
			get_identity( res, out,verbose)
		elif isinstance(ele, File):
			print('[identing]%r'%ele) if verbose else None
			stat = os_stat_safe(ele)
			res = (ele, stat.st_mtime, stat.st_size)
			out.append(res)
		elif hasattr(ele, 'to_ident'):
			ele = ele.to_ident()
			get_identity(ele, out, verbose)
		else:
			out.append(ele)
			# out.append( get_identity())
	return out