from singular_pipe._types import InputFile,OutputFile,File,TempFile, Prefix, Default
from singular_pipe._types import job_result
from singular_pipe.runner import list_flatten_strict, job_from_func, get_output_files
from singular_pipe.shell import SingularityShellCommand
from path import Path


@job_from_func
def job_trimmomatic(
	self=Default,
	prefix = File,
	FASTQ_FILE_1 = InputFile, 
	FASTQ_FILE_2 = InputFile, 
	THREADS_ = int,
	_IMAGE ='docker://quay.io/biocontainers/trimmomatic:0.35--6',
	_output = [
		File('fastq_1'),
		File('fastq_2'),
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
		File( self.output.fastq_1 ),
		File( self.output.fastq_1 + '.fail'),
		File( self.output.fastq_2 ),
		File( self.output.fastq_2 + '.fail'),
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
		CMD = list_flatten_strict(CMD)
		# res = SingularityShellCommand(CMD, )
		res = SingularityShellCommand(CMD, _IMAGE, self.output.cmd)
		return self
		# return job_result( None, CMD, self.output)

# def genepred_to_gtf():
# 	CMD = ['','cut','-f','2-']
# 	CMD = list_flatten_strict(CMD)
# 	res = SingularityShellCommand(CMD, _IMAGE)
# 	return job_result(OUTDIR, CMD, _out)
# 	# cut -f 2- temp.genepred | genePredToGtf file stdin out.gtf 

@job_from_func
def job_hisat2_index( 
	self = Default,
	prefix = File, 
	FASTA_FILE = InputFile,
	THREADS_  = int,
	_IMAGE    = "docker://quay.io/biocontainers/hisat2:2.1.0--py36hc9558a2_4",
	_output   = [
		Prefix('index_prefix'), 
		File('log'),
		File('cmd'),
	],
	):
	# _out = get_output_files(self, prefix, _output)

	# func_name = get_func_name()
	# lc = locals()
	# files = [ "{prefix}.{func_name}.{suffix}".format(suffix=suffix,**lc) for suffix in _output ]

	CMD = [
	'hisat2-build',
	 File(  FASTA_FILE),
	 Prefix(self.output.index_prefix),
	 '&>', 
	 File(  self.output.log),
	 ]
	res = SingularityShellCommand(CMD, _IMAGE, self.output.cmd)
	return self
	# return job_result( None, CMD, self.output)


@job_from_func
def job_hisat2_align(
	self   = Default,
	prefix = File,
	INDEX_PREFIX = Prefix,
	FASTQ_FILE_1 = InputFile,
	FASTQ_FILE_2 = InputFile,
	THREADS_ = int,
	_IMAGE   = "docker://quay.io/biocontainers/hisat2:2.1.0--py36hc9558a2_4",
	_IMAGE_SAMTOOLS = "docker://quay.io/biocontainers/samtools:1.10--h9402c20_2",
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
	 '-1', str( FASTQ_FILE_1),
	 '-2', str( FASTQ_FILE_2),
	 # '-U', InputFile( FASTQ_FILE_1),
	 # ['-2',InputFile( FASTQ_FILE_2) ] if FASTQ_FILE_2 else [],
	 '-S', str( self.output.bam +'.sam' ),
	 '--threads', str( THREADS_ ),
	 '--no-mixed',
	 '--rna-strandness','RF',
	 '--dta',
	 '--fr',
	 '&>', str( self.output.log),
	]
	CMD = list_flatten_strict(CMD)
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
	CMD = list_flatten_strict(CMD)
	res = SingularityShellCommand(CMD, _IMAGE_SAMTOOLS, self.output.cmd)


	CMD = [
	'samtools','sort',
	File( self.output.bam + '.unsorted'),
	'--threads', str(THREADS_),
	'-o', 
	File( self.output.bam),
	]
	CMD = list_flatten_strict(CMD)
	res = SingularityShellCommand(CMD, _IMAGE_SAMTOOLS, self.output.cmd)
	return self
	# return results[0]


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

	def get_stringtie( 
		BAM_FILE = Default,
		GTF_FILE = InputFile, 
		THREADS = int,
		_IMAGE = 'docker://quay.io/biocontainers/stringtie:2.1.1--hc900ff6_0'):
		_= '''
		stringtie 
		-p 4 
		--rf 809_S1.bam 
		-G /home/feng/ref/Arabidopsis_thaliana_TAIR10/annotation/genes.gtf 
		-o 809_S1.stringtie.gtf 
		-A 809_S1.stringtie.count &> 809_S1.stringtie.log
		'''
		_out = _stringtie_output(
			COUNT_FILE = BAM_FILE + 'stringtie.count',
			)
		CMD = [
		'stringtie',
		'-p', str(THREADS), InputFile(BAM_FILE),
		'--rf',
		'-G', InputFile(GTF_FILE),
		'-A', OutputFile(_out.COUNT_FILE),
		'&>', OutputFile(_out.COUNT_FILE + '.log'),
		]
		CMD = list_flatten_strict(CMD)
		res = SingularityShellCommand(CMD, _IMAGE)
		return job_result( _out.COUNT_FILE, CMD, self.output)

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

