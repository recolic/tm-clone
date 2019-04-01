#!/bin/bash

python3 ./daemon.py &
D_PID=$!

sleep 10

curl http://127.0.0.1:25503/ | grep '<html>'
[[ $? != 0 ]] && echo 'Failed to curl.' && exit 3

kill -9 $D_PID
exit 0

