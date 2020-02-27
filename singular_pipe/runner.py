from singular_pipe.types import File,InputFile,OutputFile, Prefix
from singular_pipe.base import get_output_files,get_func_name
import pickle
import os,sys
import json

def force_run(job, *args):
	'''
	Run a jobs regardless of whether it has a valid cache
	'''
	return cache_run(job,*args,force=True)
	_input = args
	res = job(*_input)
	return res
def cache_check(job, *args):
	'''
	Check whether there is a valid cache for this job
	'''
	return cache_run(job,*args,check_only=True)

def cache_run_verbose(job,*args):
	return cache_run(job,*args,verbose=True)
def cache_run(job, *args, check_only=False, force=False,verbose=0):
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
	_input = args
	_input = [t(v) for t,v in zip(job._input_types, _input)]
	#### calculate output files
	_output = get_output_files( job, prefix, job._output_type._fields)
	input_ident =  get_identity(_input,)
	output_ident = get_identity([Prefix(o) for o in _output])  ### consider all as prefix
	input_ident_file  = '{prefix}.{job.__name__}.input_pk'.format(**locals())
	output_ident_file = '{prefix}.{job.__name__}.output_pk'.format(**locals())
	output_cache_file = '{prefix}.{job.__name__}.output_cache'.format(**locals())

	use_cache = 0
	input_ident_dump    = pickle.dumps(input_ident)
	input_ident_changed = input_ident_dump != ( 
		open(input_ident_file,'rb').read() if file_not_empty(input_ident_file) else b'' 
		)
	output_ident_dump   = pickle.dumps(output_ident)
	output_ident_changed= output_ident_dump != (
			open(output_ident_file,'rb').read() if file_not_empty(output_ident_file) else b''
			)

	use_cache = not input_ident_changed and not output_ident_changed
	if verbose:
		print('[{func_name}]'.format(**locals()),
			json.dumps([
				('job_name',job.__name__),
			('input_ident_changed',input_ident_changed),
			('output_ident_chanegd',output_ident_changed)]
				))

	if check_only:
		return bool(use_cache)		

	if force:
		use_cache = False

	if use_cache:
		with open(output_cache_file,'rb') as f:
			res = pickle.load(f)
	else:
		res = job(*_input)
		with open(output_cache_file,'wb') as f:
			pickle.dump(res, f)
		with open(output_ident_file,'wb') as f:
			pickle.dump(get_identity(_output),f)
		with open(input_ident_file,'wb') as f:
			pickle.dump(get_identity(_input),f)
	return res


def file_not_empty(fpath):  
    '''
    Source: https://stackoverflow.com/a/15924160/8083313
    '''
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
    if file_not_empty(fname):
        return os.stat(fname)
    else:
        return _os_stat_result_null

def get_identity(lst, out = None):
	'''
	Append to file names with their mtime and st_size
	'''
	out = []
	for ele in lst:
		if isinstance(ele, Prefix):
			get_identity(ele.fileglob("*"), out)
		elif isinstance(ele, File):
			stat = os_stat_safe(ele)
			res = (ele, stat.st_mtime, stat.st_size)
			out.append(res)
	return out