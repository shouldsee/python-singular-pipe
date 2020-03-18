from spiper import make_readme,get_version
from path import Path
import sys
import subprocess
if __name__ == '__main__':
	subprocess.check_output('bash -x examples/003_remote_bash.sh 2>&1 | python3 scripts/bash_log_comment.py > examples/003_remote_bash.log.sh',shell=1)
	fn = Path(__file__).dirname().realpath()/('README.md')
	make_readme(fn).close()

