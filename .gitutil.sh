update_readme(){
	python3 build.py && git commit README.md -m build.py ; git push
}

