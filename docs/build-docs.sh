set -e
### install package first
git commit docs -mdocs || echo no_commit
rm -rf ./_docs
cp -rfT docs _docs
git checkout gh-pages
sphinx-build -b html _docs _html
cp -lfrv _html/* -t .
git add .; git commit . -m docs; git push origin gh-pages
git checkout master -f
#mv html/* .
