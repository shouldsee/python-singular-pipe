from file_tracer import InputFile,OutputFile,File,TempFile,FileTracer
from path import Path
import glob
class Prefix(Path):
	def __init__(self,*a,**kw):
		super(Prefix, self).__init__(*a,**kw)
	def fileglob(self, g):
		return glob.glob("%s%s"%(self,g))
		pass
