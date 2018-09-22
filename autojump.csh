if (`alias cwdcmd` !~ *jump.py*) then
    alias cwdcmd 'python3 $HOME/.autojump/autojump.py --add $cwd > /dev/null;' `alias cwdcmd`
endif

alias j  'cd `python3 $HOME/.autojump/autojump.py --query="\!*"`'
alias jc 'cd `python3 $HOME/.autojump/autojump.py --query="$PWD \!*"`'
alias jclean 'python3 $HOME/.autojump/autojump.py --clean'
