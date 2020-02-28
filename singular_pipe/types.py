# from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from path import Path
import glob
from collections import namedtuple

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

class File(Path):
    def __init__(self,*a,**kw):
        super(File,self).__init__(*a,**kw)



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
	def fileglob(self, g):
		# return [File(str(x)) for x in glob.glob("%s%s"%(self,g))]
		return [File(x) for x in glob.glob("%s%s"%(self,g))]
		pass
job_result = namedtuple(
	'job_result',
	[
	'OUTDIR',
	'cmd_list',
	'output']
	)
