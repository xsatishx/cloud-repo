#!/bin/bash
perl -p -i.bak_repquota -e 's|/exports/gluster\s+ext4\s+defaults,noatime,acl |/exports/gluster ext4 defaults,noatime,acl,usrjquota=aquota.user,grpjquota=aquota.group,jqfmt=vfsv0|' /etc/fstab
mount -oremount /exports/gluster
quotacheck -vgum /exports/gluster
quotaon -av
echo "repquota 8989/tcp" >> /etc/services
service xinetd restart
