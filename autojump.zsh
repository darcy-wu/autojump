export AUTOJUMP_PATH=~/.autojump

if [[ ! -d ${AUTOJUMP_PATH} ]]; then
    mkdir -p ${AUTOJUMP_PATH}
fi

if [[ ! -d ${AUTOJUMP_PATH}/jump.list ]]; then
    touch ${AUTOJUMP_PATH}/jump.list
fi

autojump_chpwd() {
    python3 $HOME/.autojump/autojump.py --add "$(pwd)" > /dev/null
}

typeset -gaU chpwd_functions
chpwd_functions+=autojump_chpwd


# default autojump command
j() {
    local output="$(python3 $HOME/.autojump/autojump.py $*)"

    if [[ -d "${output}" ]]; then
        if [ -t 1 ]; then  # if stdout is a terminal, use colors
                echo -e "\\033[31m${output}\\033[0m"
        else
                echo -e "${output}"
        fi
        cd "${output}"
    else
        echo "autojump: directory '${@}' not found"
        echo "\n${output}\n"
        echo "Try \`autojump --help\` for more information."
        false
    fi
}

jc() {
    local output="$(python3 $HOME/.autojump/autojump.py $(pwd) $*)"

    if [[ -d "${output}" ]]; then
        if [ -t 1 ]; then  # if stdout is a terminal, use colors
                echo -e "\\033[31m${output}\\033[0m"
        else
                echo -e "${output}"
        fi
        cd "${output}"
    else
        echo "autojump: directory '${@}' not found"
        echo "\n${output}\n"
        echo "Try \`autojump --help\` for more information."
        false
    fi
}

jclean() {
    python3 $HOME/.autojump/autojump.py --clean
}

