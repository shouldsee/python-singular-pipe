import importlib
from spiper._shell import pipe__getResult,pipe__getSafeResult,shellpopen
from spiper._shell import _shellcmd, shellcmd
import io,time

import json
import warnings
from spiper.base import list_flatten_strict, list_flatten
from spiper._types import File,Prefix,InputFile,InputPrefix
# from ._types import File,Prefix,InputFile,InputPrefix
import json
from path import Path
import tempfile
from spiper import VERSION




def SafeShellCommand(CMD, check=1, shell=0, encoding='utf8',stdin=None,stdout = None,stderr = None, silent=1):
	suc,stdout,stderr = _shellcmd(CMD,check,shell,encoding,stdin,stdout,stderr,silent)
	return stdout

if 1:
	def LoggedShellCommand(
		CMD, file='/dev/null', check=1, mode='w', encoding = 'utf8',
		stdin = None,stdout=None, stderr=None, 
		silent=1,
		shell=0,
		):
		'''
		CMD:
			a list of commands to be joined with ' ' and executed in bash
		file: None or a string-like filename or a file-handle
			if None, use a StringIO
		check:
			whether to raise error if the shell execution fails.
		shell:
			whether to treat CMD as a joined string or a list of string.

		'''
		if file is None:
			file = io.StringIO()
		if not isinstance(file,io.IOBase):
			file = open(file,'a',buffering=1)
		# if not shell:
		assert not shell
		CMD = list_flatten_strict(CMD)
		# shell = 1
		# with file:
		t0 = time.time()
		def _dump(o,f,**kw):
			return json.dump(list(o)+['VERSION',VERSION],f,**kw)
		_dump( ['CommandStart',-1, t0, ],file)
		file.write('\n')
		_dump( ['CommandText',] + ' '.join(CMD).splitlines(), file,indent=2)
		file.write('\n')
		# stdout = io.BytesIO(mode='w')
		# stderr = io.BytesIO()
		suc,stdout,stderr = _shellcmd(CMD,check,shell,encoding,stdin,stdout,stderr,silent)
		t1 = time.time()
		_dump( ['CommandEnd', suc, t1, (size_humanReadable(t1-t0,'s'), t1-t0)],file)
		file.write('\n')
		_dump( ['CommandResult',
			'stdout',stdout.splitlines(),
			'stderr',stderr.splitlines()],file,indent=2,default=repr)
		file.write('\n')
		file.flush()
		if check:
			if not suc:
				errmsg = 'Command "{CMD}" returned error:\n[stdout]:{stdout}\n[stderr]:{stderr}'.format(**locals())		
				raise Exception(errmsg)
			return stdout
		return suc, stdout, stderr, file


	def size_humanReadable(num,suffix='B',fmt='{0:.2f}',units=['','K','M','G','T', 'P','E'],):
	    """ Returns a human readable string reprentation of bytes,
	    Source: https://stackoverflow.com/a/43750422/8083313"""
	    if num < 1024:
	    	return fmt.format(num) + units[0] + suffix 
	    else:
	    	return size_humanReadable( num/1024.,fmt, suffix,units[1:])





if 1:
	def LoggedSingularityCommand( cmd, image, log_file,check=1,  mode='w',extra_files = None, debug =0):	
		'''
		return a tuple (executed command, command_stdout)
			cmd: a list of str-like objects that gets concatenated into a shell command
			image: a singularity image url
			extra_files: to-be-deprecated
			debug: print dbg info
		'''
		if extra_files is None:
			extra_files  = []
		cmd = ['set','-e;',cmd]
		cmd = list_flatten_strict(cmd)


		#### potential redundant
		#### all output path derives from Prefix hence only Prefix needs to be realpath
		#### for input path, realisation better be done at job calling
		out = []
		for x in cmd:
			if isinstance(x,Path):
				x = x.realpath()
			if x.startswith('/tmp'):
				warnings.warn('[singularity_run] with /tmp is unstable')
			out.append(x)
		cmd = out

		# debug = 1
		if debug: print(json.dumps(list(map(repr,cmd)),indent=4,))

		FS,modes = make_files_for(cmd)
		if debug: print(json.dumps(list(map(repr,FS)),indent=4,))

		bfs = [':'.join([f,f,m]) for f,m in zip(FS,modes)]
		# bfs = bind_files( FS + extra_files) 
		if debug: print(json.dumps(list(map(repr,bfs)),indent=4,))

		cmd_curr = [
		# '\n',
		'singularity','exec',
		'--contain',
		['--bind',','.join(bfs)] if len(bfs) else [],
		# [-1],'--bind','/tmp:/tmp',
			image,
			'bash',
			'<<EOF\n',
			cmd,
			'\nEOF',
		# '\n',
		]
		cmd_curr = list_flatten_strict(cmd_curr)
		stdout = LoggedShellCommand(cmd_curr,log_file, check,mode=mode)
		# suc,stdout
		# suc,stdout,stderr = shellcmd(cmd_curr,1,0)
		# suc , res = shellcmd(' '.join(cmd_curr),1,1)
		return (cmd_curr, stdout)

	def make_files_for(cmd):
		FS = []
		modes = []
		for F in cmd:
			if isinstance(F, (File,Prefix)):
				F = F.realpath()
				if isinstance(F, InputPrefix):
					#### if is prefix, mount the directory
					res = F.fileglob('*',1) 
					FS += res
					modes += ['ro']*len(res)
				elif isinstance(F, Prefix):
					#### if is not inputPrefix, mount the directory
					F.dirname().makedirs_p()
					FS.append( File( F.dirname() ) )
					mode = 'rw'
					modes+=[mode]
				elif isinstance(F, InputFile):
					#### if is inputFile, dont touch
					assert F.isfile(),(F,cmd)
					FS.append( F )
					modes += ['ro']					
				elif isinstance(F,File):
					#### if not inputfile, touch to makesure					
					F.touch() if not F.isfile() else None
					FS.append( F )
					modes += ['rw']
					# mode = 'rw'
				else:
					assert 0,(type(F),F)
				# FS.append(F)	
		assert len(FS) == len(modes)
		return FS,modes

	def bind_files(files):
		assert 0,'DEPRECATED'
		files = list_flatten(files)
		lst = []
		for F in files:
			#### bind the whole directory for a prefix
			if isinstance(F,Prefix):
				assert 0,(F,'run make_files_for() first', files)
			elif isinstance(F, InputFile):
				mode = 'ro'
			elif isinstance(F,File):
				mode = 'rw'
			else:
				assert 0,(F,"type %s unknown"%type(F),files,)
			F = F.realpath()
			bind_str = "%s:%s:%s"%( F, F, mode)
			lst.append( bind_str )
		return lst		
	SingularityShellCommand = LoggedSingularityCommand