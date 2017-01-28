#!/bin/bash
DIR=`pwd`
while [ 1 ]
  do
    RESULT=`ps ax | grep "starter.py"| grep -v grep | grep -v "restarter-daemon"`
    if [ "${RESULT:-null}" = null ]; then
             cd $DIR && /bin/bash $DIR/start_prod.sh 2>&1 &
    fi
    sleep 1
done