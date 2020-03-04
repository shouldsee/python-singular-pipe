build_push(){
	python3 build.py && git commit README.md -m build.py && git push
}

