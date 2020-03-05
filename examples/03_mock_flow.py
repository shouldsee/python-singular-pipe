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

@Flow
def workflow(self, prefix, seed =int , L=int, _output = []):
	print('\n[Flow running]')
	### [ToDo] (func, prefix) must be unique within each workflow
	self.data = {}
	self.data[0] = curr = self.runner(random_seq, prefix, seed, L)
	self.data[1] = curr = self.runner(transcribe, prefix, curr.output.seq,)
	self.data[2] = curr = self.runner(mutate,     prefix, curr.output.fasta)
	stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],).rstrip()
	# print(stdout)
	return self.data

import json
from singular_pipe.runner import cache_run,force_run
from singular_pipe.shell import LoggedShellCommand
def main(
	prefix = None):
	if prefix is None:
		prefix = Path('/tmp/singular_pipe.symbolic/root')
		prefix.dirname().rmtree_p()
	res = mock_run( workflow, prefix, 1, 100)	
	tree = get_downstream_tree( [Prefix(prefix+'.random_seq.seq')], strict=0)	
	### render with graphviz
	fn = Path('assets/%s.mock.dot'%__file__).basename(); fn =fn.realpath()
	g = plot_simple_graph(tree,None,0)
	g.render( fn,format='svg'); print('[see output]%s'%fn)

	res = cache_run( workflow, prefix, 1, 100 )
	tree = get_downstream_tree( [Prefix(prefix+'.random_seq.seq')], strict=0)	
	fn = Path('assets/%s.real.dot'%__file__).basename(); fn =fn.realpath()
	g = plot_simple_graph(tree,None,0)
	g.render( fn,format='svg'); print('[see output]%s'%fn)
	print(res.keys())
	# stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],)
	# print(stdout)
if __name__ == '__main__':
	main()
