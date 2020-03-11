#### get a list of changed_files
spiper get_changed_files --plain \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup

# [Flow running] mock=None
# [workflow]done
# /tmp/test_remote/root.workflow.log
# /tmp/test_remote/root.random_seq.seq
# /tmp/test_remote/root.random_seq_const.seq
# /tmp/test_remote/root.transcribe.fasta
# /tmp/test_remote/root.mutate.fasta
# /tmp/test_remote/root.source.py
# /tmp/test_remote/root.backup.subflow.random_seq.output.seq
# /tmp/test_remote/root.backup.subflow.random_seq_const.output.seq
# /tmp/test_remote/root.backup.subflow.transcribe.output.fasta
# /tmp/test_remote/root.backup.subflow.mutate.output.fasta
# /tmp/test_remote/root.backup.output.log
# /tmp/test_remote/root.backup.source.py
# /tmp/test_remote/root.backup.plot_graph.deptree_json
# /tmp/test_remote/root.backup.plot_graph.deptree_dot_txt

spiper run \
  spiper_mock_flow@https://github.com/shouldsee/spiper_mock_flow/tarball/master \
  spiper_mock_flow:run_and_backup \
  /tmp/test_remote/root,1,2,/tmp/test_remote/root.backup

# [Flow running] mock=None
# [fn] /tmp/test_remote/root.backup.plot_graph.deptree_dot_txt.svg
# [workflow]done

spiper --help >/dev/null
