repquota_check Cookbook
=================
This cookbook rolls out repquota_check for a datanode.  Still need to manually set and enable the quota on the brick.
fstab:
/dev/sdb1 /exports/gluster ext4 defaults,noatime,acl,usrjquota=aquota.user,grpjquota=aquota.group,jqfmt=vfsv0 0 2

cmds:
mount -oremount /exports/gluster
quotacheck -vguma
quotaon -av
echo "repquota 8989/tcp" >> /etc/services
