from singular_pipe import make_readme,get_version
from path import Path
import sys
if __name__ == '__main__':
	fn = Path(__file__).dirname().realpath()/('README.md')
	make_readme(fn).close()
