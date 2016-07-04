#!/bin/bash
test_dir="/glusterfs/.nagios_check"

#mkidr dir
tempdir=$(tempfile -d ${test_Dir})

rmdir $tempdir

if [ "$?" == "0" ]
then
  echo "OK"
  exit 0
else
  echo "RMDIR $tempdir failed!"
  exit 2
fi

echo "I should not be here"
exit 1

