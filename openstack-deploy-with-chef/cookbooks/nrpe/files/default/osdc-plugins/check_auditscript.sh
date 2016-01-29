#!/bin/bash
RESULT=3

AUDITS=/usr/local/var/log/auditscript

NOW=$(date +%s)

#auditscript is run every 4 days
MINHOURS=96
MAXHOURS=$(($(($MINHOURS/2))+$MINHOURS))

WARNAGE=$((60*60*$MINHOURS))
WARNAGE=$(($WARNAGE+600)) #Assuming it won't be more than ten minutes

ERRORAGE=$((60*60*$MAXHOURS))

if [ ! -d "$AUDITS" ]
then
    echo "CRITICAL - No audits appear to ever have been run"
    exit 2
fi

LASTLOG=$(ls -tr $AUDITS|tail -n 1)

LASTLOGAGE=$(($NOW-$(stat -c "%Y" $AUDITS/$LASTLOG)))

if [ $LASTLOGAGE -gt $ERRORAGE ]
then
    echo "CRITICAL - Last audit was over $MAXHOURS hours ago"
    exit 2
fi

if [ $LASTLOGAGE -gt $WARNAGE ]
then
    echo "WARN - Last audit was over $MINHOURS hours ago"
    exit 1
fi

echo "OK - last audit is recent enough"
exit 0
