from spiper import make_readme,get_version
from path import Path
import sys
import subprocess
if __name__ == '__main__':
	# cmd = '''cat examples/003_remote_bash.sh | { bash -x - | (awk '{print "### " $0}') } 2> >(stdbuf -o0 grep \+ | sed "s/^+ //g") >&1 '''
	# cmd = '''{ bash -x examples/003_remote_bash.sh | (awk '{print "### " $0}') } 2> >(stdbuf -o0 grep \+ | sed "s/^+ //g") >&1 '''
	# subprocess.check_output(cmd,executable='/bin/bash',shell=1)
	# subprocess.check_output(cmd,shell=1)
	subprocess.check_output('''python3 -m pybash --version''',shell=1,executable='/bin/bash')
	subprocess.check_output('''python3 -m pybash --log-stdout <examples/003_remote_bash.sh > examples/003_remote_bash.sh.log''',shell=1,executable='/bin/bash')
	 # | python3 scripts/bash_log_comment.py > examples/003_remote_bash.log.sh',shell=1)
	# subprocess.check_output('bash -x examples/003_remote_bash.sh 2> >(grep \\+ ) >&1  | python3 scripts/bash_log_comment.py > examples/003_remote_bash.log.sh',shell=1)
	fn = Path(__file__).dirname().realpath()/('README.md')
	make_readme(fn).close()

