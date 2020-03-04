from singular_pipe.examples.input_validation_tarball import main as _main
import singular_pipe
def main():
	singular_pipe.rcParams['dir_layout'] = 'flat'
	_main()
	s = '''
	dir_layout='flat' put meta files in same directory as data files
	'''.strip('\n')
	print(s) if __name__=='__main__' else None

	singular_pipe.rcParams['dir_layout'] = 'clean'
	_main()
	s = '''
	dir_layout='clean' put meta files according to the caller of a data file
	`caller.prefix_named.dirname()/_singular_pipe/caller.perfix_named.basename()` 
	'''.strip('\n')
	print(s) if __name__=='__main__' else None
if __name__ =='__main__':
	main()