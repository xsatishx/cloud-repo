#!/bin/bash
EXPECTED=1800
source /etc/profile

if [ -z $TMOUT ] 
then
    echo "TMOUT is not set - ERROR"
    exit 2
fi

if [ "$TMOUT" == "$EXPECTED" ]
then
    echo "TMOUT=$EXPECTED - OK"
    exit 0
fi

if [ "$TMOUT" -lt "$EXPECTED" ]
then
    echo "TMOUT less than $EXPECTED - Unexpected, but OK"
    exit 0
fi

echo "TMOUT is $TMOUT instead $EXPECTED - WARN"
exit 1
