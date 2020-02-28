#### Assuming has write access to /opt/
prefix=/opt/singularity
EXE=$prefix/bin/singularity

if [ -e /devvvvvvvvvvvvvvvvvvv ]; then
# if [ -e $EXE ]; then
	# sudo ln -sf $EXE /usr/local/bin
	echo [SKIP] singularity install because found exe at $EXE
else

_down(){
        curl -LC- "$@"
}
export DEBIAN_FRONTEND=noninteractive
 sudo -E apt-get update && \
  sudo -E apt-get install -qy build-essential \
   libssl-dev uuid-dev libseccomp-dev \
   pkg-config squashfs-tools cryptsetup

# #### downlaoad go
# export VERSION=1.13.5 OS=linux ARCH=amd64 
# _down -o go-$VERSION.tar.gz https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz
# tar -C /usr/local/ -xzf go-$VERSION.tar.gz
# # ln -sf /usr/local/go/bin/go /usr/local/bin/go
# # ls -lhtr /usr/local/go
# echo 'export GOPATH=${HOME}/go' >> ~/.bashrc 
# echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc 
# source ~/.bashrc    
# export GOPATH=${HOME}/go
# export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin
# mkdir -p $GOPATH
# go --help
go version
# echo "[installed] go"
	
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
# sudo chmod 4755 $prefix/libexec/singularity/bin/starter-suid
sudo chmod 4755 $prefix/libexec/singularity/bin/*-suid
cat $prefix/etc/singularity/singularity.conf
ls -lhtr $prefix/libexec/singularity/bin/
# sudo ln -sf /opt/singularity/bin/singularity /usr/local/bin
singularity version
