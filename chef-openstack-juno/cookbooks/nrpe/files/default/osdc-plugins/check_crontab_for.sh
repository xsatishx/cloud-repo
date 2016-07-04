#!/bin/bash
RESULT=3

if [ -z $1 ]
then
	echo "UNKNOWN - a word to get from root's crontab is needed"
	exit $RESULT
fi

TARGETWORD=$1

LINE1=$(sudo crontab -l|grep -E "^[^#].*$TARGETWORD")
LINE2=$(sudo crontab -l|grep -E "^#.*$TARGETWORD")

if [ "$LINE1" = "" ]
then
	if [ "$LINE2" = "" ]
	then
		RESULT=2
	else
		RESULT=1
	fi
else
	RESULT=0
fi


case $RESULT in
	0)
		echo "OK - $TARGETWORD in crontab"
		;;
	1)
		echo "WARNING - $TARGETWORD in crontab but commented out"
		exit 2
		;;
	2)
		echo "CRITICAL - $TARGETWORD not in crontab"
		;;
	3)
		echo "UNKNOWN"
		;;
	*)
		echo "UNKNOWN"
		;;
esac

exit $RESULT
