#!/bin/bash
CLAMSCANLOG=/var/log/clamscan.log
NOW=$(date +%s)
MAXAGE=86000 #Just shy of 1 day

if [ ! -e $CLAMSCANLOG ]
then
    echo "ERROR - clamscan log doesn't exist"
    exit 2
fi

if [ -s $CLAMSCANLOG ]
then
    echo "ERROR - Entries in the log, please review $(hostname -s):${CLAMSCANLOG}"
    exit 2
fi

LOGAGE=$(($NOW-$(date -r $CLAMSCANLOG +%s)))

if [ $LOGAGE -gt $MAXAGE ]
then
    echo "WARNING - Log is older than 23 hours"
    exit 1
fi

echo "OK - Clamscan log is recent and empty"
