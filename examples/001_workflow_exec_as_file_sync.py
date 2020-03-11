from spiper.types import Node, Flow, File

@Node  # Node is omittable, Flow() is not 
def some_node( 
		self,              #### Essn. A runtime object of type spiper.runner.Caller
		prefix,            #### Essn. A local file where a realised node would live
		input = File,      #### remembered argument,
		_some_const='foo', #### private constants, 
		_output=['txt']    #### Essn. private constants to specify output monitoring
	):

	print('... running [some_node]')
	with open(input,'r') as f:
		buf = ( f.read() + _some_const )*5 
	with open( self.output.txt, 'w') as f:
		f.write(buf)

	return self

if __name__ == '__main__':
	##### import runner functions
	from spiper.runner import cache_run, get_changed_files, get_all_files
	from pprint import pprint
	from path import Path	
	Path('/tmp/some_node/root').dirname().rmtree_p()

	fs = get_all_files(some_node, '/tmp/some_node/root', '/tmp/input_file.txt')
	print('##### all files governed by this node #######')
	pprint(fs)

	fs = get_changed_files(some_node, '/tmp/some_node/root', '/tmp/input_file.txt')
	print('#### files changed in the next execution of this node #######')      
	pprint(fs)

	print('#### write some input file ###')
	with open('/tmp/input_file.txt','w') as f: f.write('barbarfoo\n')

	print('#### actual execution #####')
	res = cache_run(some_node, '/tmp/some_node/root', '/tmp/input_file.txt')

	print('#### the second execution is skipped ###')
	res = cache_run(some_node, '/tmp/some_node/root', '/tmp/input_file.txt')
	print()

	#### the fact that the execution is skipped implies
	#### that executing this node would not change any file
	fs = get_changed_files(some_node, '/tmp/some_node/root', '/tmp/input_file.txt')
	print('#### files changed in the next execution of this node #######')      
	pprint(fs)
	assert fs == []
