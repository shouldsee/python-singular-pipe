import unittest2
import subprocess
import os,sys,shutil
from path import Path
from spiper.test.pipeline_rnaseq import job_trimmomatic, job_hisat2_index, job_hisat2_align
#from pipeline_rnaseq import *
from path import Path
import json
from spiper.runner import cache_run, cache_check, force_run, cache_run_verbose, cache_check_changed
import spiper.runner


class SharedObject(object):
	##### do not use /tmp for testing
	# DIR = Path('~/.temp/singular-pipe_test_build/').expand().makedirs_p()
	DIR = Path('~/.temp/singular-pipe_test_build/').expand().makedirs_p()
	# DIR = Path('~/.temp/singular-pipe_test_build/').expand().realpath().makedirs_p()
	# DIR = Path('/tmp/singular-pipe_test_build/').expand().makedirs_p()

	DATA_DIR = Path(spiper.__path__[0]).realpath().dirname()/'tests/data'
	# DATA_DIR = Path(__file__).realpath().dirname()/'tests/data'

from spiper.runner import job_from_func,  list_flatten
from spiper.runner import cache_run_verbose,cache_check,force_run
from spiper._types import Default,Prefix, InputFile,File
import spiper._types
from spiper._types import HttpResponseContentHeader,HttpResponse
from spiper.shell import shellcmd,LoggedShellCommand,SafeShellCommand
# from spiper.shell import pipe__getResult,pipe__getSafeResult,shellpopen
# def shellcmd(CMD, check, shell=0):
# 	suc, res = pipe__getResult(shellpopen(CMD,shell=0
# 	),CMD=CMD,check=check)
# 	return suc, res

def prefix_job(self,prefix,
	input_prefix= Prefix, 
	_output=[Prefix('out_prefix')]
	):
	for x in range(5):
		with open(self.output.out_prefix+'.%d'%x,'w') as f:
			f.write(str(x)*10)
	return self

def http_job1(
	self,prefix, 
	_response1=HttpResponseContentHeader('http://worldtimeapi.org/api/timezone/Europe/London.txt'),
	_output = [File('cache'),File('cmd')],
	):
	print(_response1.text[:20])
	return self

def http_job2(self,prefix,
	_response1=HttpResponse('GET','http://worldtimeapi.org/api/timezone/Europe/London.txt'),
	_output = [File('cache'),File('cmd')],
	):
	with open(self.output.cache, 'w') as f: f.write(_response1.text)
	res = LoggedShellCommand(['curl','-LC-',self.output.cache+'.2', _response1.url], self.output.cmd, 1)
	res = LoggedShellCommand(['curl','-LC-',self.output.cache+'.2', _response1.url], None, 1)
	return self


@job_from_func
def simple_job(self,prefix,
	# self = Default, 
	# prefix=Prefix, 
	s=str,  
	digitFile=InputFile, 
	_output=[File('out_txt')]):
	[x for x in range(10)]
	# _out = get_output_files(self, prefix, _output)
	with open( self.output.out_txt, 'w') as f:
		print(s*10)
		f.write(s*10)
	return self


class BaseCase(unittest2.TestCase,SharedObject):
	DIR = SharedObject.DIR
	DATA_DIR = SharedObject.DATA_DIR
	LEVEL = 0
	# LEVEL = 4
	def __init__(self,*a,**kw):
		super().__init__(*a,**kw)
		# shutil.rmtree(self.DIR)		
		self.DIR.rmtree_p().makedirs_p()

	def test_shellcmd(self):
		res=  shellcmd('sleep 0.01',1,1)
		res = self.assertRaisesRegex( AssertionError, '.*some_error.*', 
			shellcmd,'echo [some_error] >&2 && exit 1',1,1)	

	def test_init(self):
		_ = '''
		clean up and create a simple node
		'''
		cache_run_verbose( simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		return 
	def test_tfa_error(self):
		f = lambda: cache_run_verbose( simple_job, self.DIR/'root', 'ATG',)
		self.assertRaises(spiper._types.TooFewArgumentsError,f)

	def test_tma_error(self):
		f = lambda: cache_run_verbose( simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt','2333333random')
		self.assertRaises(spiper._types.TooManyArgumentsError, f)

	def test_tfd_error(self):
		def right_job(self = Default, prefix=File, s=str, _output=['txt']):
			pass
		job_from_func(right_job)

		def right_job(self, prefix=File, s=str, _output=['txt']):
			pass
		job_from_func(right_job)
		# self.assertRaises(spiper._types.TooFewDefaultsError, lambda: job_from_func(wrong_job))
		
		def right_job(self, prefix, s=str, _output=['txt']):
			pass
		job_from_func(right_job)

		def wrong_job(self, prefix, s, _output=['txt']):
			pass
		self.assertRaises(spiper._types.TooFewDefaultsError, lambda: job_from_func(wrong_job))

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
		# from spiper.runner import os_stat_safe
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
	def test_cacherun_output_prefix_change(self):
		_ = '''
		if the output files to a simple node changed
		trigger a recalc
		'''

		tups =(prefix_job, self.DIR/'root','/tmp/digit',)
		node = force_run(*tups,verbose=0)

		output_changed = cache_check_changed(*tups,verbose=0,check_changed=1)[1]
		assert output_changed == 0
		ofname = node.output.out_prefix+'.%d'%0
		# from spiper.runner import os_stat_safe
		# print(os_stat_safe(ofname))
		import time
		time.sleep(0.1)
		Path(ofname).touch()
		
		output_changed = cache_check_changed(*tups,verbose=0)[1]
		assert output_changed == 1,node

	@staticmethod
	def change_job():
		@job_from_func
		def simple_job(self = Default, prefix= File, s=str,  digitFile=InputFile, 
			_output=[File('out_txt')]):
			with open(  self.output.out_txt, 'w') as f:
				print(s*10)
				f.write(s*10)

				print('do something else')
			return self
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
		input_changed = cache_check_changed(*tups,verbose=0,check_changed=1)[0]
		assert input_changed == 0

		tups = (self.change_job(), self.DIR/'root', 'ATG','/tmp/digit.txt')
		input_changed = cache_check_changed(*tups,verbose=0)[0]
		assert input_changed == 1

	def test_downstream(self):
		dir_layout = 'clean'
		# import spiper
		# dir_layout = spiper.DEFAULT_DIR_LAYOUT
		(self.DIR/'root').dirname().rmtree_p()
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt',)
		force_run(*tups,dir_layout=dir_layout,verbose=0)
		tups = (simple_job, self.DIR/'job2', 'ATG', self.DIR/'root.simple_job.out_txt',)
		force_run(*tups,dir_layout=dir_layout,verbose=0)

		import spiper.graph
		# s = 
		res = spiper.graph.get_downstream_nodes([ File('/tmp/digit.txt')],strict=0,flat=0,dir_layout=dir_layout)
		print('''##### no test for nodes in get_downstream_nodes()''')
		# print(res)

		res = spiper.graph.get_downstream_files([ File('/tmp/digit.txt')],strict=0,flat=1,dir_layout=dir_layout,verbose=2)[1:]
		# res = spiper.runner.get_downstream_targets(File('/tmp/digit.txt'),strict=0,flat=0,target='all',dir_layout=dir_layout)
		expect = [
			File('~/.temp/singular-pipe_test_build/root.simple_job.out_txt'),
			File('~/.temp/singular-pipe_test_build/_spiper/root.simple_job.cache_pk'),
			File('~/.temp/singular-pipe_test_build/job2.simple_job.out_txt'),
			File('~/.temp/singular-pipe_test_build/_spiper/job2.simple_job.cache_pk'),
			]
		expect = [x.expand() for x in expect]
		assert sorted(expect) == sorted(res), json.dumps((res,expect),indent=2,default=repr)

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
		print('[param]',spiper.rcParams)
		tups = (simple_job, self.DIR/'job2', 'ATG',self.DIR/'root.simple_job.out_txt')
		job2 = force_run(*tups,verbose=0)

		res = spiper.graph.get_upstream_nodes([ File('/tmp/digit.txt')],strict=0)
		print('''##### no test for get_upstream_nodes()''')
		# print(res)

		# res ==[]
		res = spiper.graph.get_upstream_files([ File(job2.output.out_txt)],strict=0,flat=1)[1:]
		expect = [
		 InputFile('~/.temp/singular-pipe_test_build/root.simple_job.out_txt').expand(),
		 InputFile('/tmp/digit.txt')]
		expect = [x.expand() for x in expect]
		assert sorted(expect) == sorted(res), json.dumps((res,expect),indent=2)


	# def test_http_job(self):
	def test_http_job(self):
		if self.LEVEL < 1:
			return 
			# from spiper._types import HttpResponseCheckLength

		tups = (http_job1, self.DIR/'test_http_job')
		cache_run_verbose(*tups)
		res = cache_check_changed(*tups)
		assert res[0]==0

		tups = (http_job2, self.DIR/'test_http_job')
		res = cache_run_verbose(*tups)
		res = cache_check_changed(*tups)
		assert res[0]==1

	def test_loadable_subprocess(self):
		'''
		Make sure the input_json file can be loaded from other than project directory.
		'''
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		force_run(*tups, dir_layout='flat')		
		res = SafeShellCommand('''
set -e
cd /tmp/
python3 -<<EOF
import json
from path import Path
from spiper.runner import _loads,_dumps
fn = Path("~/.temp/singular-pipe_test_build/root.simple_job.input_json").expand()
d = json.load(open(fn,'r'))
x = _loads(d['ident'])
x = _loads(d['caller_dump'])
s = "_dumps(x) == d['caller_dump']"
print('#'*10 +' '+ s +' is not True, ')
print(s)
print(eval(s))
# print(x)
# print(x.job.__dict__)
EOF
cd $OLDPWD
''',1,shell=True)
		print(res)
		# print(res.decode('utf8'))

	def test_dag(self):
		tups = (simple_job, self.DIR/'root', 'ATG','/tmp/digit.txt')
		res = force_run(*tups,verbose=0)
		# tups = (simple_job, self.DIR/'job2', 'ATG', res.output.out_txt)
		# self.DIR/'root.simple_job.out_txt')
		tups = (simple_job, self.DIR/'job2', 'ATG',self.DIR/'root.simple_job.out_txt')
		force_run(*tups,verbose=0)
		pass
		return 

	def test_singularity(self, quick = 0):
		'''
		Write assertions
		'''
		# return
		# self.LEVEL = 10
		if self.LEVEL <=3:
			return
		if 0:
			shutil.rmtree(self.DIR)
		self.DIR.makedirs_p()
		DATA_DIR = self.DATA_DIR		
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
			# cache_run_verbose,
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

			if self.LEVEL<=5:
				continue

			root_prefix = self.DIR/'root'
			curr = run(
					job_trimmomatic,	# @property
	# def returned(self):
	# 	return pickle.loads(self.output_cache_file)

					root_prefix, 
					DATA_DIR/"test_R1_.fastq", 
					DATA_DIR/"test_R2_.fastq",
					THREADS)


			curr = run( job_hisat2_align,
				root_prefix,
				index.output.index_prefix,
				curr.output.fastq1,
				curr.output.fastq2,
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

