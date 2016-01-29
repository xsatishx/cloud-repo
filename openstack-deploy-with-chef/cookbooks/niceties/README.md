niceties Cookbook
=================
This cookbook rolls out small changes to the system.

Currently it does the following:

Creates a reasonable vimrc.local
Sets the default EDITOR to vim, via a script in /etc/profile.d/
Updates /etc/default/irqbalance with a hint, so it irqbalance won't spam syslog
Installs systat, then updates /etc/default/sysstat to enable sysstat collection
Creates a remote-syslog config in /etc/rsyslog.d/.  Needs a 'rsyslog':{'remote':blah,'method':blah} entry in environment
Creates a reasonable irbrc file in /etc/skel (maybe I'll move this to /home/lacadmin only?)
