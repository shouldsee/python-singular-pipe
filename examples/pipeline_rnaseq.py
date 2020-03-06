from singular_pipe.types import InputFile,OutputFile,File,TempFile, Prefix, Default
from singular_pipe.types import job_result
from singular_pipe.types import Depend
from singular_pipe.runner import list_flatten_strict, job_from_func
from singular_pipe.shell import SingularityShellCommand
from path import Path
import singular_pipe


def job_trimmomatic(
	self, prefix,
	FASTQ_FILE_1 = InputFile, 
	FASTQ_FILE_2 = InputFile, 
	THREADS_ = int,
	_IMAGE = Depend('docker://quay.io/biocontainers/trimmomatic:0.35--6'),
	_output = [
		File('fastq1'),
		File('fastq2'),
		File('log'),
		File('cmd'),
		],
	):	
		_ = '''
		trimmomatic PE -threads 4 -phred33 
		/home/feng/temp/187R/187R-S1-2018_06_27_14:02:08/809_S1_R1_raw.fastq 
		/home/feng/temp
	/187R/187R-S1-2018_06_27_14:02:08/809_S1_R2_raw.fastq 
	809_S1_R1_raw_pass.fastq 
	809_S1_R1_raw_fail.fastq 
	809_S1_R2_raw_pass.fastq 
	809_S1_R2_raw_fail.fastq 
	ILLUMINACLIP:/home/Program_NGS_sl-pw-srv01/Trimmomatic-0.32/adapters/TruSeq3-PE-2.fa
	:6:30:10 LEADING:3 TRAILING:3 MINLEN:36 SLIDINGWINDOW:4:15
		'''
		# _out = get_output_files(self, prefix, _output)

		CMD = [
		'trimmomatic','PE',
		'-threads', str(THREADS_), 
		'-phred33',
		File( FASTQ_FILE_1 ),
		File( FASTQ_FILE_2 ),
		File( self.output.fastq1 ),
		File( self.output.fastq1 + '.fail'),
		File( self.output.fastq2 ),
		File( self.output.fastq2 + '.fail'),
		'ILLUMINACLIP:'
		'/usr/local/share/trimmomatic-0.35-6/adapters/TruSeq3-PE-2.fa'
		':6:30:10',
		'LEADING:3',
		'TRAILING:3',
		'MINLEN:36',
		'SLIDINGWINDOW:4:15',
		'&>', 
		File( self.output.log)
		]
		res = SingularityShellCommand(CMD, _IMAGE, self.output.cmd)
		return self
		# return job_result( None, CMD, self.output)


def job_hisat2_index(
	self,prefix, 
	FASTA_FILE = InputFile,
	THREADS_  = int,
	_IMAGE    = Depend("docker://quay.io/biocontainers/hisat2:2.1.0--py36hc9558a2_4"),
	_output   = [
		Prefix('index_prefix'), 
		File('log'),
		File('cmd'),
	],
	):

	CMD = [
	'hisat2-build',
	 File(  FASTA_FILE),
	 Prefix(self.output.index_prefix),
	 '&>', 
	 File(  self.output.log),
	 ]
	res = SingularityShellCommand(CMD, _IMAGE, self.output.cmd)
	return self



def job_hisat2_align(
	self,prefix,
	INDEX_PREFIX = Prefix,
	FASTQ_FILE_1 = InputFile,
	FASTQ_FILE_2 = InputFile,
	THREADS_ = int,
	_IMAGE   = Depend("docker://quay.io/biocontainers/hisat2:2.1.0--py36hc9558a2_4"),
	_IMAGE_SAMTOOLS = Depend("docker://quay.io/biocontainers/samtools:1.10--h9402c20_2"),
	_output = [
		File('bam'),
		File('log'),
		File('cmd'),
	]
	):
	# _out = get_output_files(self,prefix,_output)
	results = []
	CMD = [
	 'hisat2','-x',
	 Prefix(INDEX_PREFIX),
	 '-1', File( FASTQ_FILE_1),
	 '-2', File( FASTQ_FILE_2),
	 # '-U', InputFile( FASTQ_FILE_1),
	 # ['-2',InputFile( FASTQ_FILE_2) ] if FASTQ_FILE_2 else [],
	 '-S', File( self.output.bam +'.sam' ),
	 '--threads', str( THREADS_ ),
	 '--no-mixed',
	 '--rna-strandness','RF',
	 '--dta',
	 '--fr',
	 '&>', File( self.output.log),
	]
	res = SingularityShellCommand(CMD, _IMAGE, self.output.cmd)
	# results.append(job_result( None, CMD, self.output))

	_ = '''
	samtools view /home/feng/temp/187R/187R-S1-2018_06_27_14:02:08/809_S1.sam -b --threads 4 -o 809_S1.bam
	'''
	CMD = [	
	'samtools','view',
	File( self.output.bam+'.sam'),
	'--threads',str(THREADS_),
	'-o', 
	File( self.output.bam+'.unsorted'),
	]
	res = SingularityShellCommand(CMD, _IMAGE_SAMTOOLS, self.output.cmd)


	CMD = [
	'samtools','sort',
	File( self.output.bam + '.unsorted'),
	'--threads', str(THREADS_),
	'-o', 
	File( self.output.bam),
	]
	res = SingularityShellCommand(CMD, _IMAGE_SAMTOOLS, self.output.cmd)
	return self


def job_stringtie_count(self, prefix,
	BAM_FILE = File,
	GTF_FILE = File,
	THREADS_ = int,
	_IMAGE = Depend('docker://quay.io/biocontainers/stringtie:2.1.1--hc900ff6_0'),
	_output = ['count','cmd']
	):
	_= '''
	Example run:
		stringtie 
		-p 4 
		--rf 809_S1.bam 
		-G /home/feng/ref/Arabidopsis_thaliana_TAIR10/annotation/genes.gtf 
		-o 809_S1.stringtie.gtf 
		-A 809_S1.stringtie.count &> 809_S1.stringtie.log
	'''
	CMD = [
	'stringtie',
	'-p', str(THREADS_), File(BAM_FILE),
	'--rf',
	'-G', File(GTF_FILE),
	'-A', File(self.output.count),
	]
	res = SingularityShellCommand(CMD, _IMAGE, self.output.cmd)


from singular_pipe.types import Flow
@Flow
def workflow(self, prefix, 
	hisat2_cache_dir = File,
	genome_fasta = File, 
	genome_fasta_acc = str,

	gtf_file = File,

	fastq1 = File,
	fastq2 = File,


	THREADS_ = int,
	_output=[]
	):
	self.data = {}
	self.data['index'] = self.runner(job_hisat2_index, 
		hisat2_cache_dir/genome_fasta_acc,
		genome_fasta,
		THREADS_,
		)
	self.data['trimmed'] = self.runner(
		job_trimmomatic,
		prefix,
		fastq1,
		fastq2,
		THREADS_,
		)
	self.data['aligned'] = self.runner(
		job_hisat2_align,
		prefix,
		self.data['index'].output.index_prefix,
		self.data['trimmed'].output.fastq1,
		self.data['trimmed'].output.fastq2,
		THREADS_,
		)
	self.data['count'] = self.runner(
		job_stringtie_count,
		prefix,
		self.data['aligned'].output.bam,
		gtf_file,
		THREADS_,
		)
	return self.data

def get_fasta(self, prefix,
	_depends = [Depend('curl'),Depend('gzip')],
	_resp = singular_pipe.types.HttpResponseContentHeader('https://hgdownload.soe.ucsc.edu/goldenPath/currentGenomes/Wuhan_seafood_market_pneumonia_virus/bigZips/chromFa.tar.gz'),
	_output = ['fasta','cmd']):
	with (self.prefix_named/'_temp').makedirs_p() as d:
		CMD = ['curl','-LC0',_resp.url,
		'|','tar','-xvzf-',]
		stdout = singular_pipe.types.LoggedShellCommand(CMD)
		res = d.glob('*.fa')
		assert len(res)==1
		res[0].move(self.output.fasta)
	d.rmtree_p()

from singular_pipe.types import LoggedShellCommand
LoggedSingularityCommand = SingularityShellCommand
def get_genepred(self,prefix,
	_resp = singular_pipe.types.HttpResponseContentHeader('https://hgdownload.soe.ucsc.edu/goldenPath/currentGenomes/Wuhan_seafood_market_pneumonia_virus/database/ncbiGene.txt.gz'),
	_IMAGE = Depend('docker://quay.io/biocontainers/ucsc-genepredtogtf:377--h35c10e6_2'),
	_output = ['genepred','gtf','cmd'],
	):
	CMD = ['curl','-LC0',_resp.url,
	'|','gzip -d | cut -f2- >',self.output.genepred,
	]

	LoggedShellCommand(CMD, self.output.cmd,mode='w')
	CMD = ['genePredToGtf','file',self.output.genepred, self.output.gtf]
	LoggedSingularityCommand(CMD, _IMAGE, self.output.cmd,mode='a')

	# return 

if __name__ == '__main__':
	from singular_pipe.runner import force_run,cache_run
	data = {}
	data['fasta'] = cache_run(get_fasta,'~/.temp/0305',)
	data['gtf']   = cache_run(get_genepred,'~/.temp/0305',)
	data['flow1'] = cache_run(workflow,
		'~/.temp/0305.sample1',
		'~/.temp/hisat2/', 
		data['fasta'].output.fasta,
		'wuhan-ncov19',
		data['gtf'].output.gtf,
		'./tests/data/test_R1_.fastq',
		'./tests/data/test_R2_.fastq',
		2,
		)


if 0:
	################################### TBC afterwards ############################
	@job_from_func
	def get_picard_dedup(
		self = Default,
		prefix = Prefix,
		BAM_FILE = InputFile,
		_IMAGE = 'docker://quay.io/biocontainers/picard:2.21.9--0',
		_output = ['bam'],
		):
		_ ='''
		java -XX:ParallelGCThreads=4 -jar /home/feng/envs/pipeline_Bd/jar/MarkDuplicates.jar 
		I=/home/feng/temp/187R/187R-S1-2018_06_27_14:02:08/809_S1.sorted.bam O=809_S1_dedup.bam M=809_S1.dupstat.log REMOVE_DUPLICATES=true
		'''
		_out = _picard_dedup_output(
			BAM_FILE = OutputFile( rstrip( InputFile(BAM_FILE),'.bam') +'.dedup.bam'),
			)
		PROG = 'singularity exec docker://quay.io/biocontainers/picard:2.21.9--0 picard'.split()
		CMD = [
		'picard',
		'MarkDuplicates',
		# 'java','-XX:ParallelGCThreads=%s'%THREADS,
		'I=%s'% InputFile(  BAM_FILE ),
		'O=%s'% OutputFile(_out.BAM_FILE ),
		'M=%s'% OutputFile(_out.BAM_FILE +'.log') ,
		]
		CMD = list_flatten_strict(CMD)
		res = SingularityShellCommand(CMD, _IMAGE)
		return job_result( _out.BAM_FILE, CMD, self.output)



	def get_htseq():
		_ = '''
		#### htseq-count is too slow and not used
		htseq-count 
		-s reverse 
		-f bam 809_S1.bam 
		/home/feng/ref/Arabidopsis_thaliana_TAIR10/annotation/genes.gtf 
		-r pos -o 809_S1.htseq.sam >809_S1.htseq.count 2>809_S1.htseq.log
		'''
		pass

