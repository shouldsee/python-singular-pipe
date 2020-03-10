set -e
### install package first

#mkdir _build_docs; cp -rft _build_docs
git checkout master
git commit docs -mdocs || echo no_commit
rm -rf ./_docs
cp -rfT docs _docs
git checkout gh-pages
sphinx-build -b html _docs _html
cp -lfr _html/* -t .
cp -lfr _html/ -T ../singular_pipe_docs
git add .; git commit . -m docs; git push origin gh-pages
git checkout master -f
#mv html/* .
#git checkout 
