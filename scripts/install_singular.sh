#### Assuming has write access to /opt/
# prefix=${1:-/opt/singularity}
set -e
prefix=${1:-$HOME/.local}
EXE=$prefix/bin/singularity
NCORE=$( nproc 2>/dev/null || echo 1 )

mkdir -p $prefix/bin

# if [ -e /devvvvvvvvvvvvvvvvvvv ]; then
if [ -e $EXE ]; then
  # sudo ln -sf $EXE /usr/local/bin
  echo [SKIP] singularity install because found exe at $EXE
else

_down(){
        curl -LC- "$@"
}


#### install go
export GIMME_GO_VERSION=1.13.5
eval "$(curl -sL https://raw.githubusercontent.com/travis-ci/gimme/master/gimme |  bash)"
go version



#### do not use sudo if making a local install
apt-get download squashfs-tools
dpkg -x squashfs-tools*.deb _temp
cp -lf _temp/usr/bin/* $prefix/bin


# sudo -E echo ask for sudo access for apt
# export DEBIAN_FRONTEND=noninteractive
#  sudo -E apt-get update && \
#   sudo -E apt-get install -qy build-essential \
#    libssl-dev uuid-dev libseccomp-dev \
#    pkg-config squashfs-tools cryptsetup

##### downlaoad go
VERSION=3.5.3
URL=https://github.com/singularityware/singularity/releases/download/v$VERSION/singularity-$VERSION.tar.gz
_down -o $(basename $URL) $URL
tar -xf singularity-$VERSION.tar.gz

{
  cd singularity
  # go run mlocal/checks/version.go
  mkdir -p $prefix
  ./mconfig --prefix=$prefix --without-suid && \
    make -C ./builddir && \
    make -C ./builddir install
    cd ..
}
fi

{
  echo mksquashfs path = `which mksquashfs`
  echo cryptsetup path = `which cryptsetup`
} >> $prefix/etc/singularity/singularity.conf
cat $prefix/etc/singularity/singularity.conf

# sudo ln -sf $EXE /usr/local/bin
$EXE version
# $EXE exec --bind `pwd`:/srv  --pwd /srv docker://quay.io/biocontainers/hisat2:2.1.0--py36hc9558a2_4 hisat2 --help 
$EXE --verbose --debug exec docker://python:2.7.17-alpine python -V

ln -sf $EXE -t $HOME/.local/bin || echo linking failed #### [Fragile]
ls -lhtr $prefix/libexec/singularity/bin/

