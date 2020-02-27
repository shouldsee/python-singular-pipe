export DEBIAN_FRONTEND=noninteractive
 apt-get update && \
  apt-get install -qy build-essential \
   libssl-dev uuid-dev libseccomp-dev \
   pkg-config squashfs-tools cryptsetup


_down(){
        curl -LC- "$@"
}


#### downlaoad go
export VERSION=1.13.5 OS=linux ARCH=amd64 
_down -o go-$VERSION.tar.gz https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz
tar -C /usr/local/ -xzf go-$VERSION.tar.gz
ln -sf /usr/local/go/bin/go /usr/local/bin/go

# echo 'export GOPATH=${HOME}/go' >> ~/.bashrc && \
#     echo 'export PATH=/usr/local/go/bin:${PATH}:${GOPATH}/bin' >> ~/.bashrc && \
#     source ~/.bashrc    

VERSION=3.5.3
URL=https://github.com/singularityware/singularity/releases/download/v$VERSION/singularity-$VERSION.tar.gz
_down -o $(basename $URL) $URL
tar xvf singularity-$VERSION.tar.gz

{
	cd singularity
	./mconfig && \
    make -C ./builddir && \
    make -C ./builddir install
    cd ..
}

singularity --help