#!/bin/bash


luks_disks() {

  cd /dev

  root_disk=$(mount | perl -n -e 'm|/dev/(\S+)\d+\s+on\s+/boot| && print "$1\n"')

  for x in $(ls sd*[^0-9])
  do

    #Check if its not the device mounted as /boot
    if [ "$x" == "$root_disk" ]
    then
      continue
    fi

    #Make sure its not part of an mdadm array
    if [[ $(cat /proc/mdstat  | grep $x) ]]
    then 
        continue
    fi

    #Make sure its not an SSD
    smartctl --all $x | grep "Device Model" 2>/dev/null  | grep SSD &>/dev/null
    if [ "$?" != "0" ]
    then
      echo /dev/${x}1 
      parted /dev/${x} mklabel gpt || exit 1
      parted /dev/${x} mkpart xfs xfs 64M 100% || exit 1
      yes | cryptsetup --cipher aes-xts-plain64 --hash sha512 --iter-time 5000 --use-random --verify-passphrase luksFormat --key-file /etc/luks/keyfile /dev/${x}1 || exit 1
      cryptsetup --key-file /etc/luks/keyfile luksOpen /dev/${x}1 luks_${x}1 || exit 1
      echo "luks_${x}1 /dev/${x}1 /etc/luks/keyfile luks,cipher=aes-xts-plain64,hash=sha512" >> /etc/crypttab.bak
      echo "luks_${x}1 UUID=$(cryptsetup luksUUID /dev/${x}1)  /etc/luks/keyfile luks,cipher=aes-xts-plain64,hash=sha512" >> /etc/crypttab.UUID
    fi
  done
}

luks_disks
