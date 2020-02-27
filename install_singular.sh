_down(){
	curl -LC0 "$@"
}

VERSION=3.5.3
URL=https://github.com/singularityware/singularity/releases/download/v$VERSION/singularity-$VERSION.tar.gz
_down -o $(basename $URL) $URL
tar xvf singularity-$VERSION.tar.gz

{
	cd singularity
	./mconfig && \
    make -C ./builddir && \
    sudo make -C ./builddir install
}
