#!/bin/bash
COUNTFILE=/usr/local/var/log/check_iptables_lines

if [ ! -e "$COUNTFILE" ]
then
  echo 0 > $COUNTFILE
fi

REGLINES=$(<$COUNTFILE) #this is how many we had last time
MINLINES=$(echo $REGLINES/2|bc -l|cut -d "." -f 1) #This is completely arbitrary
LINES=$(grep -c -vE "^$|^#" /etc/iptables.conf)

if [ $LINES -lt $MINLINES ]
then
    echo "Too few lines in iptables, probably not valid"
    exit 2
fi

if [ $LINES -lt $REGLINES ]
then
    echo "Fewer lines ($LINES found vs expected $REGLINES)"
    exit 1
fi

echo "iptables appears proper"
echo $LINES > $COUNTFILE
exit 0
