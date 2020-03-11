
from path import Path
from spiper.runner import cache_run, force_run
def simplest_node(self,prefix,_output=[]):
	print('Running node:%r'%self)
	return self ### return Runtime Caller as output is beneficial

if __name__ == '__main__':
	print('\n### running')
	prefix = Path('/tmp/bulid_spiper/root')
	prefix.dirname().rmtree_p()
	cache_run(simplest_node, prefix )
	cache_run(simplest_node, prefix )
	print()
	
	s = '''
	### comment
	expect: 
	Running node:spiper.runner.Caller(dotname='__main__.simplest_node',prefix_named=File('/tmp/bulid_spiper/root.simplest_node'))
	Running node:spiper.runner.Caller(dotname='__main__.simplest_node',prefix_named=File('/tmp/bulid_spiper/root.simplest_node'))
	
	got:
	Running node:spiper.runner.Caller(dotname='__main__.simplest_node',prefix_named=File('/tmp/bulid_spiper/root.simplest_node'))

	The second run accessed cache
	'''
	print(s)
	pass


def less_simple_node( self, prefix, seq=str, _output=['txt']):
	with open(self.output.txt,'w') as f:
		print('writing %s to %r'%(seq,self.output.txt))
		f.write(seq * 10)
	return self

if __name__ == '__main__':
	print('\n### running')

	prefix = Path('/tmp/bulid_spiper/root')
	prefix.dirname().rmtree_p()
	cache_run( less_simple_node, prefix, 'ATCG' )
	cache_run( less_simple_node, prefix, 'ATCG' )
	cache_run( less_simple_node, prefix, 'ATCG' )
	cache_run( less_simple_node, prefix, 'GCTA' )
	s = '''
	### comment
	expect:
	writing ATCG to File('/tmp/bulid_spiper.less_simple_node.txt')
	writing ATCG to File('/tmp/bulid_spiper.less_simple_node.txt')
	writing ATCG to File('/tmp/bulid_spiper.less_simple_node.txt')
	writing GCTA to File('/tmp/bulid_spiper.less_simple_node.txt')

	got:
	writing ATCG to File('/tmp/bulid_spiper.less_simple_node.txt')
	writing GCTA to File('/tmp/bulid_spiper.less_simple_node.txt')

	Becuase cache file is loaded for the two middle evaluations

	'''
	print(s.strip('\n'))
	pass

from spiper._types import File
from spiper.shell import LoggedShellCommand
def make_tar( self, prefix, input_file=File, _output=['tar_gz'] ):
	with input_file.dirname() as d:
		print('taring %r'%d)
		stdout = LoggedShellCommand(['tar','-zvcf',self.output.tar_gz, '*'], '/dev/null')
		# ,mode='a')
	return self
	# print(stdout)


if __name__ == '__main__':
	prefix = Path('/tmp/bulid_spiper/root')
	prefix.dirname().rmtree_p()

	caller = cache_run(less_simple_node, prefix, 'ATCG')
	res0 = caller
	print('[res0.output.txt]:%r'%res0.output.txt)
	caller = cache_run(make_tar,         prefix, res0.output.txt)
	caller = cache_run(make_tar,         prefix, res0.output.txt)  #marked#


	caller = cache_run(less_simple_node, prefix, 'GATC')
	caller = cache_run(make_tar,         prefix, res0.output.txt)
	print('[done]')
	s = '''
	## got
	writing ATCG to File('/tmp/bulid_spiper/root.less_simple_node.txt')
	[res0.output.txt]:File('/tmp/bulid_spiper/root.less_simple_node.txt')
	taring File('/tmp/bulid_spiper')
	writing GATC to File('/tmp/bulid_spiper/root.less_simple_node.txt')
	taring File('/tmp/bulid_spiper')
	[done]

	## Note make_tar() is detecting the change of res0.output.txt and skipped the #marked# evaluation
	'''