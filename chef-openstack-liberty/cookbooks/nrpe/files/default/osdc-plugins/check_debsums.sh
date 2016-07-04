#!/bin/bash
WARNINGS=$(mktemp)
sudo /usr/bin/debsums -sl --ignore-permissions >& $WARNINGS

MG="missing file"
NG="no md5sums"

MISSING_C=$(grep -c "$MG" $WARNINGS)
NO_C=$(grep -c "$NG" $WARNINGS)
MISSING_NO_C=$(grep -cE "$MG|$NG" $WARNINGS)

TOTAL_C=$(grep -cE "^" $WARNINGS)

rm -f $WARNINGS

PROBLEM_C=$(($TOTAL_C-$MISSING_NO_C))

#echo "MISSING_C=$MISSING_C"
#echo "NO_C=$NO_C"
#echo "PROBLEM_C=$PROBLEM_C"

if [ "$PROBLEM_C" -gt 0 ]
then
  echo "ERROR: problems detected with debsums"
  exit 2
fi

if [ "$MISSING_NO_C" -gt 0 ]
then
  echo "WARNING: $MISSING_C files missing, $NO_C files missing md5sums"
  exit 1
fi

echo "OK - all packages verify with debsums"

exit 0
