#!/usr/bin/env bash

# echo "c Activating Conda environment"
# Initialize our own variables:
function interrupted(){
  kill -TERM $PID
}
trap interrupted TERM
trap interrupted INT


if [ -d "$HOME/miniconda3/" ]; then
  myconda="$HOME/miniconda3"
elif [ -d "$HOME/anaconda3/" ]; then
  myconda="$HOME/anaconda3"
else
  #myconda="specify conda path"
  echo "c REQUIRES CONDA"
  exit 5
fi

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('$myconda/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "$myconda/etc/profile.d/conda.sh" ]; then
        . "$myconda/etc/profile.d/conda.sh"
    else
        export PATH="$myconda/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

conda activate dpdb_env 

# $myconda/envs/rb/bin/python $solver_cmd &

solver_cmd="python subsolver.py $@"

env $solver_cmd &
PID=$!
wait $PID
exit_code=$?

exit $exit_code
