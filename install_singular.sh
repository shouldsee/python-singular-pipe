#### Assuming has write access to /opt/
prefix=${1:-/opt/singularity}
EXE=$prefix/bin/singularity
NCORE=$( nproc 2>/dev/null || echo 1 )

# if [ -e /devvvvvvvvvvvvvvvvvvv ]; then
if [ -e $EXE ]; then
	# sudo ln -sf $EXE /usr/local/bin
	echo [SKIP] singularity install because found exe at $EXE
else

_down(){
        curl -LC- "$@"
}

sudo -E echo ask for sudo access for apt
#### install go
export GIMME_GO_VERSION=1.13.5
eval "$(curl -sL https://raw.githubusercontent.com/travis-ci/gimme/master/gimme |  bash)"
go version

export DEBIAN_FRONTEND=noninteractive
 sudo -E apt-get update && \
  sudo -E apt-get install -qy build-essential \
   libssl-dev uuid-dev libseccomp-dev \
   pkg-config squashfs-tools cryptsetup

##### downlaoad go
VERSION=3.5.3
URL=https://github.com/singularityware/singularity/releases/download/v$VERSION/singularity-$VERSION.tar.gz
_down -o $(basename $URL) $URL
tar -xf singularity-$VERSION.tar.gz

{
	cd singularity
	go run mlocal/checks/version.go
	mkdir -p /opt/singularity
	./mconfig --prefix=$prefix --without-suid && \
    make -C ./builddir && \
    make -C ./builddir install
    cd ..
}
fi


sudo ln -sf $EXE /usr/local/bin
cat $prefix/etc/singularity/singularity.conf
ls -lhtr $prefix/libexec/singularity/bin/
singularity version
# sudo chmod 4755 $prefix/libexec/singularity/bin/starter-suid
# sudo chmod 4755 $prefix/libexec/singularity/bin/*-suid
# sudo ln -sf /opt/singularity/bin/singularity /usr/local/bin
