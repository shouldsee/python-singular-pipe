'''
Showing how Prefix differs from File
'''
from spiper.types import File,Prefix,Path
from spiper.runner import cache_run_verbose, cache_run

from spiper.types import LoggedShellCommand
from spiper.runner import cache_check_changed,cache_run_verbose,force_run,cache_run
import spiper

def gen_files(self, prefix, 
	_seq = 'AGCTTCGTC',
	 _output=[
	 	File('out_txt')]):
	with open(self.output.out_txt,'w') as f:
		f.write( _seq * 10 )
	return self

def tarball_dangerous_cache(self,prefix, 
	input_prefix = File,
	_output=[
	File('tar_gz'),
	File('cmd')]):
	with input_prefix.dirname(): 
		stdout = LoggedShellCommand([
			'tar', '-cvzf', self.output.tar_gz, input_prefix.basename()+'*',
			], 
			self.output.cmd)
	return self	

def tarball_prefix_cache(self,prefix, 
	input_prefix = Prefix,
	_output=[
		File('tar_gz'),
		File('cmd')]):
	
	with input_prefix.dirname(): 
		stdout = LoggedShellCommand([
			'tar', '-cvzf', self.output.tar_gz, input_prefix.basename()+'*',
			], 
			self.output.cmd)
	return self

def main(force_run=force_run,prefix=None):
	# spiper.rcParams['dir_layout'] = dir_layout
	if prefix is None:
		prefix = Path('/tmp/spiper.test_run/root')
		prefix.dirname().rmtree_p()


	print('\n---------------------Run1---\n## got') if __name__ == '__main__' else None
	res1 = force_run(gen_files, prefix,verbose=0)
	res2 = force_run(tarball_dangerous_cache, prefix, res1.prefix_named, verbose=1)
	
	res1 = force_run(gen_files, prefix,verbose=0)
	res2 = force_run(tarball_dangerous_cache, prefix, res1.prefix_named, verbose=1)

	s = '''
## expect 
[cache_run] {"job_name"="tarball_dangerous_cache"_"input_ident_changed"=1_"output_ident_chanegd"=0}

	* This change to input is ignored because tarball_dangerous_cache(input_prefix=File) would not expand to match the files during input validation The type specified in def line will be used for detecting a timestamp/filesize change	
	
	'''.strip()
	print(s) if __name__ == '__main__' else None


	print('---------------------Run2---\n## got') if __name__ == '__main__' else None

	res1 = force_run(gen_files, prefix)
	res2 = force_run(tarball_prefix_cache, prefix, res1.prefix_named, verbose=1)
	
	res1 = force_run(gen_files, prefix)
	res2 = force_run(tarball_prefix_cache, prefix, res1.prefix_named, verbose=1)
	
	s = '''
## expect 
[cache_run] {"job_name"="tarball_prefix_cache"_"input_ident_changed"=1_"output_ident_chanegd"=0}

	* Because tarball_prefix_cache(input_prefix=Prefix) is expanded into the appropriate files during input validation.
	* Note that the Prefix only expands into a shallow match and does not recurse into sub-directory during input validation
	'''.strip()
	print(s) if __name__ == '__main__' else None
	print('------Output Directory. (dir_layout={spiper.rcParams.dir_layout})--------\n'.format(spiper=spiper),
		LoggedShellCommand(['echo [ls]',prefix,'&&','ls','-lhtr',prefix.dirname(),],'/dev/null'))
	return res1,res2

if __name__ == '__main__':
	main()
