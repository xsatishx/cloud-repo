#!/bin/bash
NUM_DRIVES_PRE=$(cat drives.txt)
NUM_DRIVES_CUR=$(sudo dmsetup status | grep "crypt" | wc -l)
echo ${NUM_DRIVES_CUR} >> drives.txt
DEBUG=0

if [ ${DEBUG} -eq 1 ]; then
  echo ${NUM_DRIVES_CUR}
  echo ${NUM_DRIVES_PRE}
fi

if [ ! -s drives.txt  ]; then
        echo "CRITICAL | No Encrypted drives on this server.."
        exit 2
fi


if [ ${NUM_DRIVES_CUR} -lt ${NUM_DRIVES_PRE} ]; then
        echo "CRITICAL | Number of drives differs from last check.."
        exit 2
else
        echo "OK | ${NUM_DRIVES_CUR} partitions currently encrypted.."
fi

rm -rf drives.txt
NUM_DRIVES_CUR=$(sudo dmsetup status | grep "crypt" | wc -l)
echo ${NUM_DRIVES_CUR} >> drives.txt
