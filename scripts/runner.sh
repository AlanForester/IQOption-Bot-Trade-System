#!/bin/bash
DIR=`pwd`
sh $DIR/restarter-daemon.sh 2>&1 > $DIR/logs/yogamerchant-runner.log &
set NOHUP