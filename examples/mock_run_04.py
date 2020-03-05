'''
Symbolic run construct .outward_edges, .input_json and .output_json as usual 
but skip the creation of actual output files.
A symbolic node is a node with all output_files being empty
'''
import singular_pipe
from singular_pipe.types import File,Prefix,HttpResponse, HttpResponseContentHeader
from singular_pipe.shell import LoggedShellCommand
from singular_pipe.runner import mock_run
from singular_pipe.graph import get_downstream_tree
from singular_pipe.graph import plot_simple_graph
from path import Path
from singular_pipe.types import Flow

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
	print('[Flow runs in %r]'%self.runner)
	curr = self.runner(random_seq, prefix, seed, L)
	curr = self.runner(transcribe, prefix, curr.output.seq,)
	curr = self.runner(mutate,     prefix, curr.output.fasta)
	return self

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
	g = plot_simple_graph(tree,None,0)
	g.render('assets/%s.mock.dot'%Path(__file__).basename(),format='svg')

	res = cache_run( workflow, prefix, 1, 100 )
	tree = get_downstream_tree( [Prefix(prefix+'.random_seq.seq')], strict=0)	
	g = plot_simple_graph(tree,None,0)
	g.render('assets/%s.real.dot'%Path(__file__).basename(),format='svg')

	stdout = LoggedShellCommand(['ls -lhtr',prefix.dirname()],)
	print(stdout)
if __name__ == '__main__':
	main()
