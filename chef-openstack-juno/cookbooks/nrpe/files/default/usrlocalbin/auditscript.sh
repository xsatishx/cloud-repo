#!/bin/bash
export SERVER=$(hostname)
export DATE=$(date +"%m%d%y")
export NAL=/usr/local/var/log/auditscript/
LOG=$NAL/nih_audit_${SERVER}_${DATE}.txt
echo "Previously Executed Commands $SERVER $DATE" >> $LOG
lastcomm >> $LOG
echo "Total Connect Time $SERVER $DATE" >> $LOG
ac --daily-totals >> $LOG
echo "Connect Time by user $SERVER $DATE" >> $LOG
ac --individual-totals >> $LOG
echo "Resource usage by command $SERVER $DATE" >> $LOG
sa -u >> $LOG
echo "Resource usage by user $SERVER $DATE" >> $LOG
sa -m >> $LOG
exit
