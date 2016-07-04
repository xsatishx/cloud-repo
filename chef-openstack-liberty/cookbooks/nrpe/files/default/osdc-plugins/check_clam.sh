#!/bin/bash
if sudo clamscan --cross-fs=no -r --no-summary --infected /
then
  echo "OK - Clamscan"
  exit 0
else
  echo "ERROR - Clamscan"
  exit 2
fi
