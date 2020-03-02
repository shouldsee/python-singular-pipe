import unittest2
import subprocess
import os,sys,shutil
from path import Path
from pipeline_rnaseq import job_trimmomatic, job_hisat2_index, job_hisat2_align
#from pipeline_rnaseq import *
from path import Path
import json
from singular_pipe.runner import cache_run, cache_check, force_run, cache_run_verbose, cache_check_changed
import singular_pipe.runner

class SharedObject(object):
	# DIR = Path('$HOME/.temp/singular-pipe_test_build/').makedirs_p()
	DIR = Path('~/.temp/singular-pipe_test_build/').expand().makedirs_p()
	##### do not use /tmp for testing
	# DIR = Path('/tmp/singular-pipe_test_build/').expand().makedirs_p()

	# DIR = Path('$HOME/.temp/singular-pipe_test_build/').expand().makedirs_p()
	shutil.rmtree(DIR)
	DIR.makedirs_p()
	DATA_DIR = Path(__file__).realpath().dirname()/'tests/data'

from singular_pipe.base import job_from_func, get_output_files, list_flatten
from singular_pipe.runner import cache_run_verbose,cache_check,force_run
from singular_pipe.types import Default,Prefix, InputFile,File
import singular_pipe.types

@job_from_func
def simple_job(
	self = Default, 
	prefix=Prefix, 
	s=str,  
	digitFile=InputFile, 
	_output=[File('out_txt')]):
	_out = get_output_files(self, prefix, _output)
	with open( _out.out_txt, 'w') as f:
		print(s*10)
		f.write(s*10)
	# return self

_ = '''
[ToDo]
	- [ ] logging the command executed into .cmd file
	- [x] adding an outward_pk file to complement input_pk and auto-sync
		- the outward_pk should record identity of the output file and input file.
		- the input_ident is useful 
	- [x] produce a dependency graph
		- get_upstream_files()
		- get_downstream_nodes()
	- [ ] capture stderr and stdout of subprocess.check_output(), with optional log file.

[ToDo]
    - adding tests for Prefix InputPrefix OutputPrefix
in get_idenity()
	InputPrefix should not match nothing
	OutputPrefix could match empty 
in bind_files()
	InputPrefix should not match nothing
	OutputPrefix could match empty
these two functions are kind of similar, but treat OutputPrefix differently
	in get_identity(), An empty OutputPrefix would reduce to []
	in bind_files(), An empty OutputPreix would cause the whole directory to be mounted
additionally, 
	get_identity() needs to expand objects other than Prefix and File, including Params
	bind_files() only consider local files for now

[ToDo]capturing get_identity() of Static params
[ToDo]illustrating the different between vars
static:    argname starts with '_' --> value is static constant of function,            must not override
temporary: argname endswith '_'    --> value is a type, discarded for cache-validation, necessary arg  
validated: argname otherwise       --> value is a type, kept for cache-validation,      ncessary

### [add-test] for  
def test_tempvar_change()  --> assert input_change == 0 
def test_statvar_change()  --> raise tma error
def test_validvar_change() --> assert input_change == 1

[add-test] for get_output_files() to preserve types from the original _output list.
  e.g. dont cast File into Prefix through namedtuple() in job_from_func()

### [ToDo] get_output_files(), 
### currently the returned _output consider all _output object as Prefix, 
because _output is a list and there isn't a way of specifying their type.

'''
class BaseCase(unittest2.TestCase,SharedObject):
	DIR = SharedObject.DIR
	DATA_DIR = SharedObject.DATA_DIR

	def test_init(self):
		_ = '''
		clean up and create a simple node
		'''
		cache_run_verbose( simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		return 
	def test_tfa_error(self):
		f = lambda: cache_run_verbose( simple_job, self.DIR/'root', 'ATG',)
		self.assertRaises(singular_pipe.types.TooFewArgumentsError,f)

	def test_tma_error(self):
		f = lambda: cache_run_verbose( simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt','2333333random')
		self.assertRaises(singular_pipe.types.TooManyArgumentsError, f)

	def test_tfd_error(self):
		def right_job(self = Default, prefix=Prefix, s=str, _output=['txt']):
			pass
		job_from_func(right_job)

		def wrong_job(self, prefix=Prefix, s=str, _output=['txt']):
			pass
		self.assertRaises(singular_pipe.types.TooFewDefaultsError, lambda: job_from_func(wrong_job))
		
		def wrong_job(self, prefix, s=str, _output=['txt']):
			pass
		self.assertRaises(singular_pipe.types.TooFewDefaultsError, lambda: job_from_func(wrong_job))

	def test_cacherun_use_cache(self):
		_ = '''
		if the input files / params to a simple node changed,
		then trigger a recalc
		'''
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		force_run(*tups,verbose=0)
		result = cache_run(*tups,verbose=0)
		# input_changed = cache_check_changed(*tups,verbose=0)[0]
		# assert input_changed == 0

		# result = cache_run(*tups,verbose=0)
		# assert input_changed == 1

	def test_cacherun_input_change(self):
		_ = '''
		if the input files / params to a simple node changed,
		then trigger a recalc
		'''
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		force_run(*tups,verbose=0)
		input_changed = cache_check_changed(*tups,verbose=0)[0]
		assert input_changed == 0

		import time
		time.sleep(0.1)
		Path(tups[-1]).touch()
		input_changed = cache_check_changed(*tups,verbose=0)[0]
		assert input_changed == 1

		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		force_run(*tups,verbose=0)
		input_changed = cache_check_changed(*tups,verbose=0)[0]
		assert input_changed == 0

		tups = (simple_job, self.DIR/'root', 'ATGC','/tmp/digit.txt')
		input_changed = cache_check_changed(*tups,verbose=0)[0]
		assert input_changed == 1

	def test_cacherun_output_change(self):
		_ = '''
		if the output files to a simple node changed
		trigger a recalc
		'''
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		force_run(*tups,verbose=0)

		output_changed = cache_check_changed(*tups,verbose=0)[1]
		assert output_changed == 0

		ofname = self.DIR/'root.simple_job.out_txt'
		# from singular_pipe.runner import os_stat_safe
		# print(os_stat_safe(ofname))
		import time
		time.sleep(0.1)
		# subprocess.check_output(['touch','-m',ofname])
		# with open(ofname,'w') as f:
		# 	pass
		Path(ofname).touch()
		# print(os_stat_safe(ofname))
		
		output_changed = cache_check_changed(*tups,verbose=0)[1]
		assert output_changed == 1

	@staticmethod
	def change_job():
		@job_from_func
		def simple_job(self = Default, prefix=Prefix, s=str,  digitFile=InputFile, 
			_output=[File('out_txt')]):
			_out = get_output_files(self, prefix, _output)
			with open( _out.out_txt, 'w') as f:
				print(s*10)
				f.write(s*10)

				print('do something else')
			# return self #### construct a Caller with .output attr
		return simple_job


	def test_cacherun_code_change(self):
		_ = '''
		the defition of a script change is ambiguous
		here we used a tuple to identify a function
			(
			func_code.co_code
			func_code.co_consts
			)
		'''
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		force_run(*tups,verbose=0)
		input_changed = cache_check_changed(*tups,verbose=0)[0]
		assert input_changed == 0

		tups = (self.change_job(), self.DIR/'root', 'ATG','/tmp/digit.txt')
		input_changed = cache_check_changed(*tups,verbose=0)[0]
		assert input_changed == 1

	def test_downstream(self):
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		force_run(*tups,verbose=0)
		tups = (simple_job, self.DIR/'job2', 'ATG', self.DIR/'root.simple_job.out_txt')
		force_run(*tups,verbose=0)

		res = singular_pipe.runner.get_downstream_nodes(File('/tmp/digit.txt'),strict=0,flat=0)
		print('''##### no test for nodes in get_downstream_nodes()''')
		# print(res)

		res = singular_pipe.runner.get_downstream_files(File('/tmp/digit.txt'),strict=0,flat=1)
		expect = [
			File('~/.temp/singular-pipe_test_build/root.simple_job.out_txt'),
			File('~/.temp/singular-pipe_test_build/_singular_pipe/root.simple_job.cache_pk'),
			File('~/.temp/singular-pipe_test_build/job2.simple_job.out_txt'),
			File('~/.temp/singular-pipe_test_build/_singular_pipe/job2.simple_job.cache_pk'),
			]
		expect = [x.expand() for x in expect]
		assert expect == res, json.dumps((res,expect),indent=2)
	def test_caller_struct(self):
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		res = force_run(*tups,verbose=0)
		print('#### test_caller_struct() not impled')
		return
		tups = (simple_job, self.DIR/'job2', 'ATG', res.output.out_txt)
		tups = (simple_job, self.DIR/'job2', 'ATG',self.DIR/'root.simple_job.out_txt')
		force_run(*tups,verbose=0)

	def test_upstream(self):
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		res = force_run(*tups,verbose=0)
		# tups = (simple_job, self.DIR/'job2', 'ATG', res.output.out_txt)
		# self.DIR/'root.simple_job.out_txt')
		tups = (simple_job, self.DIR/'job2', 'ATG',self.DIR/'root.simple_job.out_txt')
		force_run(*tups,verbose=0)

		res = singular_pipe.runner.get_upstream_nodes(File('/tmp/digit.txt'),strict=0)
		print('''##### no test for get_upstream_nodes()''')
		# print(res)

		# res ==[]
		res = singular_pipe.runner.get_upstream_files(File(self.DIR/'job2.simple_job.out_txt'),strict=0,flat=1)
		expect = [
		 InputFile('~/.temp/singular-pipe_test_build/root.simple_job.out_txt').expand(),
		 InputFile('/tmp/digit.txt')]
		expect = [x.expand() for x in expect]
		assert expect == res, json.dumps((res,expect),indent=2)

	def test_dag(self):
		pass


		return 
	def test_singularity(self, quick = 0):
		'''
		Write assertions
		'''
		return
		if 0:
			shutil.rmtree(self.DIR)
		self.DIR.makedirs_p()
		DATA_DIR = self.DATA_DIR		
		# print(DATA_DIR)
		# assert 0
		# print(DATA_DIR.glob("*"))
		# WKDIR  = Path('/opt/singular-pipe_test_build/').makedirs_p()
		THREADS = 2
		_ = '''
		singularity pull docker://quay.io/singularity/singularity:v3.5.3-slim
		'''

		##### we want to avoid re-calculating the output if they already exist and is intact
		##### this is done by storing an identity information on disk 
		##### this identity information is calculated from the outputted files
		##### which could be md5sum or timestamp
		for run in [
			force_run, 
			cache_run_verbose,
			cache_run_verbose,
			]:
			index = run(job_hisat2_index,
				self.DIR / 'phiX.fasta.prefix',
				DATA_DIR/'phiX.fasta',
				THREADS
				)

			tups = (job_hisat2_index,
				self.DIR / 'phiX.fasta.prefix',
				DATA_DIR/'phiX.fasta',
				THREADS
				)
			print('[CACHE_CHECK]%s'%cache_check(*tups))
			# print( get_identity( index.output) )
			# assert 0
			import pickle
			with open('/tmp/test1.pkl' ,'wb') as f:
				pickle.dump(index,f)

			if quick:
				continue

			root_prefix = self.DIR/'root'
			curr = run(
					job_trimmomatic,
					root_prefix, 
					DATA_DIR/"test_R1_.fastq", 
					DATA_DIR/"test_R2_.fastq",
					THREADS)


			curr = run( job_hisat2_align,
				root_prefix,
				index.output.index_prefix,
				curr.output.fastq_1,
				curr.output.fastq_2,
				THREADS)

	# test_basic()
import pdb
import traceback
def debugTestRunner(post_mortem=None):
	"""unittest runner doing post mortem debugging on failing tests"""
	if post_mortem is None:
		post_mortem = pdb.post_mortem
	class DebugTestResult(unittest2.TextTestResult):
		def addError(self, test, err):
			# called before tearDown()
			traceback.print_exception(*err)
			post_mortem(err[2])
			super(DebugTestResult, self).addError(test, err)
		def addFailure(self, test, err):
			traceback.print_exception(*err)
			post_mortem(err[2])
			super(DebugTestResult, self).addFailure(test, err)
	return unittest2.TextTestRunner(resultclass=DebugTestResult)


if __name__ == '__main__':

	print('[testing]%s'%__file__)
	# with SharedObject.DIR:
	if '--pdb' in sys.argv:
		del sys.argv[sys.argv.index('--pdb')]
		unittest2.main(testRunner=debugTestRunner())
	else:
		unittest2.main(testRunner=None)

