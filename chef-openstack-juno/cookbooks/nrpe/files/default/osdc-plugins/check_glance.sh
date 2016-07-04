#!/bin/bash
F=/usr/local/var/log/glancetime

if [ ! -e $F ]
then
  echo "Error, no log file at $F"
  exit 2
fi

RAWSECONDS=$(cut -d "," -f 1 $F)
TIMERUN=$(cut -d "," -f 2 $F)
SIXHOURS=21600

NOW=$(date +%s)

#Stupid rounding
SECONDS=$(echo $RAWSECONDS|cut -d "." -f 1)
DEC=$(echo $RAWSECONDS|cut -d "." -f 2|cut -c 1)
if [ $DEC -gt 5 ]
then
    SECONDS=$(($SECONDS+1))
fi


MESSAGE=""
VAL=0

if [ $(($NOW-$TIMERUN)) -gt $SIXHOURS ]
then
    MESSAGE="No test in over 6 hours"
    VAL=1
fi

if [ $SECONDS -gt 60 ]
then
    MESSAGE="$SECONDS seconds to download 1GB image - CRITICAL - $MESSAGE"
    VAL=2
fi

if [ "$MESSAGE" == "" ]
then
    MESSAGE="Downloaded 1GB image in $SECONDS seconds - OK"
fi

echo $MESSAGE
exit $VAL
