#!/bin/bash

xfs_disks() {

      for x in $(ls /dev/mapper/luks_*)
      do
          drive=$( echo $x  | perl -ne 'm|(/dev/mapper)/(luks_\S+)| && print "$2\n"')
          mapper_path=$( echo $x  | perl -ne 'm|(/dev/mapper)/(luks_\S+)| && print "$1\n"')

          mkfs.xfs -f  ${mapper_path}/${drive} || exit 1
          mkdir -p /srv/node/${drive} 
          echo "${mapper_path}/${drive}   /srv/node/${drive}    xfs    noatime,nodiratime,nobarrier,logbufs=8     0 0" >> /etc/fstab
      done
}

xfs_disks
mount -a -txfs
