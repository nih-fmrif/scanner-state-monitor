
test -s ~/.alias && . ~/.alias || true

# source ~/.login

PATH=$PATH:/sbin:/usr/sbin:$HOME/RTafni/bin:$HOME/RTafni/bin/AFNI:.
export PATH

LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib64:/usr/lib64:$HOME/RTafni/lib
export LD_LIBRARY_PATH

# User specific aliases and functions

alias    rm='rm -i'
alias    mv='mv -i'
alias    cp='cp -i'
alias  here='ls -alF'
alias    vi="vim -i NONE -C"

export LANG=C

export LESSHISTFILE=-

