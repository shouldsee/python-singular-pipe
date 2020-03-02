# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from path import Path
import glob
from collections import namedtuple
import os

class TooManyArgumentsError(RuntimeError):
	pass
class TooFewArgumentsError(RuntimeError):
	pass
# class NotEnoughArgumentsError(RuntimeError):
# 	pass
class TooFewDefaultsError(RuntimeError):
	pass
def Default(x):
	'''
	A dummy "class" mocked with a function
	'''
	return x

# class Static(object):
# 	def __init__(self,a):
# 		pass
_os_stat_result_null = os.stat_result([0 for n in range(os.stat_result.n_sequence_fields)])
def os_stat_safe(fname):
	if os.path.isfile(fname):
		return os.stat(fname)
	else:
		return _os_stat_result_null


class File(Path):
	def __init__(self,*a,**kw):
		super(File,self).__init__(*a,**kw)
	def to_ident(self):
		stat = os_stat_safe(self)
		res = (self, stat.st_mtime, stat.st_size)
		return res


class TempFile(File):
	def __init__(self,*a,**kw):
		super(TempFile,self).__init__(*a,**kw)
	pass

class InputFile(File):
	def __init__(self,*a,**kw):
		super(InputFile,self).__init__(*a,**kw)
	pass

class OutputFile(File):
	def __init__(self,*a,**kw):
		super(OutputFile,self).__init__(*a,**kw)
	pass

class Prefix(Path):
	def __init__(self,*a,**kw):
		super(Prefix, self).__init__(*a,**kw)
	def fileglob(self, g, strict):
		res = [File(x) for x in glob.glob("%s%s"%(self,g))]
		if strict:
			assert len(res),'(%r,%r) expanded into nothing!'% (self,g)
		# return [File(str(x)) for x in glob.glob("%s%s"%(self,g))]
		return res
		pass
class InputPrefix(Prefix):
	def __init__(self,*a,**kw):
		super( InputPrefix,self).__init__(*a,**kw)

class OutputPrefix(Prefix):
	def __init__(self,*a,**kw):
		super( OutputPrefix,self).__init__(*a,**kw)

job_result = namedtuple(
	'job_result',
	[
	'OUTDIR',
	'cmd_list',
	'output']
	)


def IdentFile(config, prefix, job, suffix):
	prefix = Prefix(prefix)

	if config == 'clean':
		pre_dir = prefix.dirname()
		pre_base = prefix.basename()
		input_ident_file  = '{pre_dir}/_singular_pipe/{pre_base}.{job.__name__}.{suffix}'.format(**locals())
	elif config == 'flat':
		input_ident_file = '{prefix}.{job.__name__}.{suffix}'.format(**locals())
		pass
	return File(input_ident_file)
	pass

class CacheFile(OutputFile):
	pass