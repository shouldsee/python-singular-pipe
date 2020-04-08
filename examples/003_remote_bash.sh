#### get a list of changed_files
# rm -rfv /tmp/test_remote/*
set -euo pipefail; commit=7c317b

spiper get_changed_files \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root 1 2 /tmp/test_remote/root.backup

### reduce redundancy in bash call
ARR=(spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root 1 2 /tmp/test_remote/root.backup )

spiper get_changed_files ${ARR[@]}

spiper run ${ARR[@]}

spiper get_changed_files ${ARR[@]}
# [No files changed by this workflow]'

spiper caller_show_deps ${ARR[@]}
# [File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py')]

spiper caller_show_deps --which_flow ${ARR[@]}
# [(File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py'),
#   [File('spiper:///tmp/test_remote/root.source.py'),
#    File('spiper:///tmp/test_remote/root.backup.source.py')])]
spiper file_show_deps /tmp/test_remote/root.transcribe.fasta

### ignore --plain to enable ANSI color
spiper caller_show_log ${ARR[@]} --plain                       

spiper file_show_log /tmp/test_remote/root.transcribe.fasta --plain  

spiper --help >/dev/null
