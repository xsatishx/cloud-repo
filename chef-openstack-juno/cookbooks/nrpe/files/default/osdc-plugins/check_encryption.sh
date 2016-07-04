#!/bin/bash

if sudo cryptsetup luksDump /dev/sdb?|egrep "^Cipher name:.*aes"
then
  echo "Using AES encryption - OK"
  exit 0
fi

