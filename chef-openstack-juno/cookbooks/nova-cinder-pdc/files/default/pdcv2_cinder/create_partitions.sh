#!/bin/bash
       parted /dev/sdb mklabel gpt
       parted /dev/sdc mklabel gpt 
       parted /dev/sdb mkpart xfs xfs 64M 100%
       parted /dev/sdc mkpart xfs xfs 64M 100%
       yes | cryptsetup --cipher aes-xts-plain64 --hash sha512 --iter-time 5000 --use-random --verify-passphrase luksFormat  --key-file /etc/luks/keyfile  /dev/sdb1
       yes | cryptsetup --cipher aes-xts-plain64 --hash sha512 --iter-time 5000 --use-random --verify-passphrase luksFormat  --key-file /etc/luks/keyfile  /dev/sdc1

   	cryptsetup --key-file /etc/luks/keyfile luksOpen /dev/sdb1 brick_sdb1
	cryptsetup --key-file /etc/luks/keyfile luksOpen /dev/sdc1 brick_sdc1
        
        pvcreate /dev/mapper/brick_sdb1 
        pvcreate /dev/mapper/brick_sdc1
        vgcreate cinder-volumes-sdb1 /dev/mapper/brick_sdb1
        vgcreate cinder-volumes-sdc1 /dev/mapper/brick_sdc1
