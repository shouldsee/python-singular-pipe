from pipeline_rnaseq import job_trimmomatic, job_hisat2_index, job_hisat2_align
#from pipeline_rnaseq import *
from path import Path
DATA_DIR = Path(__file__).dirname()/'tests/data'
# print(DATA_DIR.glob("*"))
WKDIR  = Path('/deps/test_build/').makedirs_p()
THREADS = 2
from singular_pipe.runner import cache_run, cache_check, force_run
from pipeline_rnaseq import get_output_files
_ = '''
singularity pull docker://quay.io/singularity/singularity:v3.5.3-slim
'''
# from pipeutil.runner import cache_run, cache_check, force_run
# run = force_run
# run = cache_run
# for run in [cache_run,force_run]:

##### we want to avoid re-calculating the output if they already exist and is intact
##### this is done by storing an identity information on disk 
##### this identity information is calculated from the outputted files
##### which could be md5sum or timestamp
for run in [
	force_run, 
	lambda *a:cache_run(*a, verbose=1),
	lambda *a:cache_run(*a, verbose=1) ]:

	index = run(job_hisat2_index,
		'/deps/index/phiX.fasta.hisat2',
		DATA_DIR/'phiX.fasta'
		)

	tups = (job_hisat2_index,
		'/deps/index/phiX.fasta.hisat2',
		# DATA_DIR/'phiX.fasta',
		DATA_DIR/'phiX.fasta'
		)
	print('[CACHE_CHECK]%s'%cache_check(*tups))
	# print( get_identity( index.output) )
	# assert 0
	import pickle
	with open('test1.pkl' ,'wb') as f:
		pickle.dump(index,f)

	continue 
	root_prefix = WKDIR/'root'
	curr = run(job_trimmomatic,
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


	'''
	singularity exec docker://quay.io/biocontainers/ucsc-genepredtogtf:377--h35c10e6_2 bash -c  "cut -f 2- temp.genepred | genePredToGtf file stdin out.gtf"
	'''