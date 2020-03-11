from spiper.examples.input_validation_tarball import main as _main
import spiper
def main():
	spiper.rcParams['dir_layout'] = 'flat'
	_main()
	s = '''
	dir_layout='flat' put meta files in same directory as data files
	'''.strip('\n')
	print(s) if __name__=='__main__' else None

	spiper.rcParams['dir_layout'] = 'clean'
	_main()
	s = '''
	dir_layout='clean' put meta files according to the caller of a data file
	`caller.prefix_named.dirname()/_spiper/caller.perfix_named.basename()` 
	'''.strip('\n')
	print(s) if __name__=='__main__' else None
if __name__ =='__main__':
	main()