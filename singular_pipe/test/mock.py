import unittest2
from path import Path
import singular_pipe
from singular_pipe.test.graph import tarball_main
from singular_pipe.types import LoggedShellCommand,File
from singular_pipe.runner import mock_run,cache_run
from pprint import pprint
class Case(unittest2.TestCase):
	def test_mock_overwrite(self):
		# assert 0
		prefix = None
		if prefix is None:
			prefix = File('/tmp/singular_pipe.symbolic/root')
			
		prefix.dirname().rmtree_p()	
		_d = singular_pipe.rcParams.copy()
		singular_pipe.rcParams['dir_layout'] = 'clean'

		tarball_main( mock_run, prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd.old.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz.empty.mock'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz.old.mock')]


		# tarball_main( lambda *a:cache_run(*a,check_changed=2), prefix)
		tarball_main( cache_run, prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz')]

		tarball_main( mock_run , prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz')]



		with open((prefix + '.gen_files.out_txt'),'w') as f:
			f.write('100'*2000)
		tarball_main( mock_run , prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
	 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt.old.mock'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd.old.mock'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz'),
	 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz.old.mock')]


		tarball_main( cache_run, prefix)
		fs = sorted(prefix.fileglob('*',0,0)); print(pprint(fs))
		assert fs == [
		 File('/tmp/singular_pipe.symbolic/root.gen_files.out_txt'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_dangerous_cache.tar_gz'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.cmd'),
		 File('/tmp/singular_pipe.symbolic/root.tarball_prefix_cache.tar_gz')]

		# res = LoggedShellCommand(['ls -lhtr',prefix+'*'])
		# .fileglob('*'),])
		# print(res)
		# prefix
		# tarball_main( mock_run , prefix)
		# assert 0
		# (prefix.dirname()/'root.tarball_dangerous_cache.tar_gz').touch()
		# self.assertRaises(singular_pipe._types.OverwriteError, tarball_main, mock_run, prefix)
		singular_pipe.rcParams.update(_d)

