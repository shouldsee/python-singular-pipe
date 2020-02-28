from singular_pipe.types import File,InputFile,OutputFile, Prefix
from singular_pipe.types import TooManyArgumentsError
import singular_pipe.types

from singular_pipe.base import get_output_files,get_func_name
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



def ident_changed(ident, ident_file):
	ident_dump     = pickle.dumps(ident)
	ident_dump_old = open(ident_file,'rb').read() if file_not_empty(ident_file) else b''
	return ident_dump != ident_dump_old
def ident_dump(ident, ident_file):
	with open(ident_file,'wb') as f:
		pickle.dump( ident,  f )
def _raise(e):
	raise e
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

	input_ident_file  = '{prefix}.{job.__name__}.input_pk'.format(**locals())
	output_ident_file = '{prefix}.{job.__name__}.output_pk'.format(**locals())
	output_cache_file = '{prefix}.{job.__name__}.output_cache'.format(**locals())

	#### calculate input tuples
	### cast types for inputs
	_input = args
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
			_tmp.append(t(v))
	print(_dump()) if verbose>=2 else None
	_input = _tmp
	_job_args = _input[:] ### pass to job(*_job_args)

	#### skip the prefix when calculating _input
	assert job._input_names[0] =='prefix',job._input_names
	del _input[0]

	_input += [ (job._origin_code.co_code,job._origin_code.co_consts) ]


	#### calculate output files
	### cast all files all as prefix
	### here we add cache_file as a constitutive output.
	_output = get_output_files( job, prefix, job._output_type._fields)
	# print('[out1]',_output)
	_output = [Prefix(o) for o in _output] + [OutputFile(output_cache_file)]
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
		with open(output_cache_file,'rb') as f:
			result = pickle.load(f)

	else:
		result = job(*_job_args)
		ident_dump( result, output_cache_file)
		ident_dump( get_identity(_output), output_ident_file)
		ident_dump( get_identity(_input), input_ident_file)
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
	for ele in lst:
		if isinstance(ele, Prefix):
			res = ele.fileglob("*")
			print('[expanding]\n  %r\n  %r'%(ele,res)) if verbose else None
			get_identity( res, out,verbose)
		elif isinstance(ele, File):
			print('[identing]%r'%ele) if verbose else None
			stat = os_stat_safe(ele)
			res = (ele, stat.st_mtime, stat.st_size)
			out.append(res)
		else:
			out.append(ele)
	return out