
test -s ~/.alias && . ~/.alias || true

# source ~/.login

export PATH=$PATH:/sbin:/usr/sbin:/home/rtadmin/RTafni/bin:/home/rtadmin/RTafni/bin/AFNI:.

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib64:/usr/lib64:/home/rtadmin/RTafni/lib

# User specific aliases and functions

alias    rm='rm -i'
alias    mv='mv -i'
alias    cp='cp -i'
alias  here='ls -alF'
alias    vi="vim -i NONE -C"

export LANG=C

export LESSHISTFILE=-

