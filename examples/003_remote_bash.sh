#### get a list of changed_files
commit=7c317b
spiper get_changed_files \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root 1 2 /tmp/test_remote/root.backup

### or use a comma-separated list of arguments
spiper get_changed_files \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit \
  spiper_mock_flow:run_and_backup \
  --comma /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup



### reduce redundancy
ARR=(spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/$commit \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root 1 2 /tmp/test_remote/root.backup )

spiper get_changed_files ${ARR[@]}
# [Flow running] mock=None
# [workflow]done
# [File('/tmp/test_remote/root.workflow.log'),
#  File('/tmp/test_remote/root.random_seq.seq'),
#  File('/tmp/test_remote/root.random_seq_const.seq'),
#  File('/tmp/test_remote/root.transcribe.fasta'),
#  File('/tmp/test_remote/root.mutate.fasta'),
#  File('/tmp/test_remote/root.source.py'),
#  File('/tmp/test_remote/root.backup.subflow.random_seq.output.seq'),
#  File('/tmp/test_remote/root.backup.subflow.random_seq_const.output.seq'),
#  File('/tmp/test_remote/root.backup.subflow.transcribe.output.fasta'),
#  File('/tmp/test_remote/root.backup.subflow.mutate.output.fasta'),
#  File('/tmp/test_remote/root.backup.output.log'),
#  File('/tmp/test_remote/root.backup.source.py'),
#  File('/tmp/test_remote/root.backup.plot_graph.deptree_json'),
#  File('/tmp/test_remote/root.backup.plot_graph.deptree_dot_txt')]

spiper run ${ARR[@]}


# [Flow running] mock=None
# [fn] /tmp/test_remote/root.backup.plot_graph.deptree_dot_txt.svg
# [workflow]done

spiper get_changed_files ${ARR[@]}
# [No files changed by this workflow]'

spiper get_all_deps ${ARR[@]}
# [File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py')]

spiper get_all_deps --which_flow ${ARR[@]}
# [(File('/home/user/.local/lib/python3.5/site-packages/spiper_mock_flow.py'),
#   [File('spiper:///tmp/test_remote/root.source.py'),
#    File('spiper:///tmp/test_remote/root.backup.source.py')])]

spiper --help >/dev/null
