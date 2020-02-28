import unittest2
import subprocess
import os,sys,shutil
from path import Path
from pipeline_rnaseq import job_trimmomatic, job_hisat2_index, job_hisat2_align
#from pipeline_rnaseq import *
from path import Path
from singular_pipe.runner import cache_run, cache_check, force_run, cache_run_verbose

class SharedObject(object):
	# DIR = Path('$HOME/.temp/singular-pipe_test_build/').makedirs_p()
	DIR = Path('~/.temp/singular-pipe_test_build/').expand().makedirs_p()
	##### do not use /tmp for testing
	# DIR = Path('/tmp/singular-pipe_test_build/').expand().makedirs_p()

	# DIR = Path('$HOME/.temp/singular-pipe_test_build/').expand().makedirs_p()
	shutil.rmtree(DIR)
	DIR.makedirs_p()
	DATA_DIR = Path(__file__).realpath().dirname()/'tests/data'

class BaseCase(unittest2.TestCase,SharedObject):
	DIR = SharedObject.DIR
	DATA_DIR = SharedObject.DATA_DIR

	def test_init(self):
		_ = '''
		clean up and create a simple node
		'''
		return 
	def test_cacherun_input_change(self):
		_ = '''
		if the input files to a simple node changed,
		then trigger a recalc
		'''
		pass
	def test_cacherun_output_change(self):
		_ = '''
		if the output files to a simple node changed
		trigger a recalc
		'''
		pass
	def test_cacherun_code_change(self):
		_ = '''
		the defition of a script change is ambiguous
		here we used a tuple to identify a function
			(
			func_code.co_code
			func_code.co_consts
			)
		'''
		pass
	def test_basic(self, quick =1):
		'''
		Write assertions
		'''
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
				DATA_DIR/'phiX.fasta'
				)

			tups = (job_hisat2_index,
				self.DIR / 'phiX.fasta.prefix',
				DATA_DIR/'phiX.fasta'
				)
			print('[CACHE_CHECK]%s'%cache_check(*tups))
			# print( get_identity( index.output) )
			# assert 0
			import pickle
			with open('test1.pkl' ,'wb') as f:
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

