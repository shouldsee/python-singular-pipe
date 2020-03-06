'''
Symbolic run construct .outward_edges, .input_json and .output_json as usual 
but skip the creation of actual output files.
A symbolic node is a node with all output_files being empty
'''
import singular_pipe
from singular_pipe.types  import Node,Flow
from singular_pipe.types  import Path, File, Prefix
from singular_pipe.types  import HttpResponse, HttpResponseContentHeader
from singular_pipe.types  import LoggedShellCommand
from singular_pipe.runner import mock_run
from singular_pipe.graph  import get_downstream_tree, plot_simple_graph

import random
def random_seq(self, prefix, seed = int, L = int, _output=['seq']):
	random.seed(seed)
	with open(self.output.seq,'w') as f:
		f.write('>random_sequence\n')
		buf = ''
		for i in range(L):
			buf += 'ATCG'[int(random.random()*4)]
		f.write(buf+'\n')
	return self


def transcribe(self, prefix, input = File, _output=['fasta']):
	with open(input,'r') as fi:
		with open(self.output.fasta,'w') as fo:
			fo.write(fi.read().replace('T','U'))
	return self

@Node
def mutate(self, prefix, input=File, _seed = 1, _output=['fasta']):
	random.seed(_seed)
	with open(input,'r') as fi:
		with open(self.output.fasta,'w') as fo:
			buf = list(fi.read())
			random.shuffle(buf)
			fo.write(''.join(buf))
	return self

from singular_pipe.types import SubflowOutput

@Flow
def workflow(self, prefix, seed =int , L=int, _output = [
	# SubflowOutput( 'mutate', ),### monitor the subflow status
	File('log'),
	]):
	_ = '''
	A workflow is not a Node()
	'''
	print('\n[Flow running] mock=%s'%getattr(self.runner.func,'__name__','None'))
	### [ToDo] (func, prefix) must be unique within each workflow
	# self.data = {}
	curr = self.runner(random_seq, prefix,  seed,  L)
	curr = self.runner(transcribe, prefix,  curr.output.seq,)
	curr = self.runner(mutate,     prefix,  curr.output.fasta)
	stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],).rstrip()
	return self

import json
from singular_pipe.runner import cache_run,force_run,is_mock_file
from singular_pipe.shell import LoggedShellCommand
from singular_pipe.types import File,CacheFile
def main(
	prefix = None):
	if prefix is None:
		prefix = Path('/tmp/singular_pipe.symbolic/root')
		prefix.dirname().rmtree_p()
	print('\n...[start]%r'%prefix)
	# print(workflow.output)
	res = mock_run( workflow, prefix, 1, 100,verbose=1)
	from pprint import pprint
	pprint(res.get_changed_files())

	fs = res.get_changed_files()
	exp = [
	  File('/tmp/singular_pipe.symbolic/root.workflow.log'),
	  CacheFile('/tmp/singular_pipe.symbolic/_singular_pipe/root.workflow.cache_pk'),
	  File('/tmp/singular_pipe.symbolic/root.random_seq.seq'),
	  CacheFile('/tmp/singular_pipe.symbolic/_singular_pipe/root.random_seq.cache_pk'),
	  File('/tmp/singular_pipe.symbolic/root.transcribe.fasta'),
	  CacheFile('/tmp/singular_pipe.symbolic/_singular_pipe/root.transcribe.cache_pk'),
	  File('/tmp/singular_pipe.symbolic/root.mutate.fasta'),
	  CacheFile('/tmp/singular_pipe.symbolic/_singular_pipe/root.mutate.cache_pk')
	  ]
	assert sorted(fs) == sorted(exp),pprint(list(zip(sorted(fs),sorted(exp))))
	res = cache_run( workflow, prefix, 1, 100,verbose=1)

	File('/tmp/singular_pipe.symbolic/root.workflow.log').touch()
	res = mock_run( workflow, prefix, 1, 100,verbose=1)
	fs = (res.get_changed_files())
	assert fs == [
	  File('/tmp/singular_pipe.symbolic/root.workflow.log'),
 	  CacheFile('/tmp/singular_pipe.symbolic/_singular_pipe/root.workflow.cache_pk')
 	]


	res = mock_run( workflow, prefix, 2, 100,verbose=1)
	fs = (res.get_changed_files())
	assert fs == exp

	print('\n...[Done]')
	stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],).rstrip()
	print(stdout)	
	of1 = res.subflow.mutate.output.fasta
	of2 = res['subflow']['mutate']['output']['fasta'] 
	of3 = res.get_subflow('mutate').get_output('fasta')
	assert of1 is of2 is of3	
	print(of3)

	#### this is more visually pleasant 
	tree = get_downstream_tree( [Prefix(prefix+'.random_seq.seq')], strict=0)	
	### render with graphviz
	fn = Path('assets/%s.mock.dot'%__file__).basename(); fn =fn.realpath()
	g = plot_simple_graph(tree,None,0)
	g.render( fn,format='svg'); print('[see output]%s'%fn)

	res = force_run( workflow, prefix, 1, 100 )
	tree = get_downstream_tree( [Prefix(prefix+'.random_seq.seq')], strict=0)	
	fn = Path('assets/%s.real.dot'%__file__).basename(); fn =fn.realpath()
	g = plot_simple_graph(tree,None,0)
	g.render( fn,format='svg'); print('[see output]%s'%fn)
	# print(res.keys())
	# stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],)
	# print(stdout)
if __name__ == '__main__':
	main()
