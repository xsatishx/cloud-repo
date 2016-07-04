#!/bin/bash
WAITLEFT=300 #That's 5 minutes, but hey
WAITLEFT=30 #That's 30 seconds now
#Should be a bit better
DIR=$(mktemp -d)
PIDS=""

OUTPUT=/dev/null
for MP in $(mount|grep -E "fuse.glusterfs|nfs|cifs"|cut -d " " -f 3)
do
        ls $MP > /dev/null &
  echo $MP > $DIR/$!
        PIDS="$PIDS $!"
done

SLEEP=5
PASSES=0
while [ $WAITLEFT -gt 1 ] 
do
        NPIDS=""
        for PID in $PIDS
        do  
                if kill -0 $PID >& /dev/null
                then
                        SLEEP=$(($SLEEP+2))
                        NPIDS="$NPIDS $PID"
                else
                        echo "Mount for $PID completed" >& $OUTPUT
                fi  
        done
        PIDS=$NPIDS
        if [ $SLEEP == 0 ] 
        then
                WAITLEFT=0
        else
    #Sleep progressively longer
    SLEEP=$(($SLEEP+$PASSES))
    PASSES=$(($PASSES+1))
                WAITLEFT=$(($WAITLEFT-$SLEEP))
                echo "Sleeping $SLEEP seconds out of $WAITLEFT seconds to wait on $PIDS" > $OUTPUT
                sleep $SLEEP
                SLEEP=0
        fi  
done

HUNG=0
for PID in $PIDS
do
        echo "Mount for $(<$DIR/$PID) hung"
        kill -9 $PID >& /dev/null
        HUNG=$(($HUNG+1))
done

rm -rf $DIR

if [ $HUNG == 0 ] 
then
        echo "OK - no hanging network mounts"
        exit 0
else
        exit 2
fi
