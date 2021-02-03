# turn on bash's job control
set -m
dagit -h 0.0.0.0 -p 3000 -f main.py &
dagster-daemon run

fg %1
