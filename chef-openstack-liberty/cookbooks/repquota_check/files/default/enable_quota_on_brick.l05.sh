#!/bin/bash
perl -p -i.bak_repquota -e 's|/exports/glusterfs ext4\s+defaults,acl\s+0\s+2|/exports/glusterfs ext4 defaults,noatime,acl,usrjquota=aquota.user,grpjquota=aquota.group,jqfmt=vfsv0 0 2|' /etc/fstab
mount -oremount /exports/glusterfs
quotacheck -vgum /exports/glusterfs
quotaon -av
echo "repquota 8989/tcp" >> /etc/services
service xinetd restart
