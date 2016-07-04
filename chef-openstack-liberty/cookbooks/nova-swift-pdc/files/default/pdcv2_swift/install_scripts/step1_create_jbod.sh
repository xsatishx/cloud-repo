#!/bin/bash

delete_raid5() {
   cd /root/install_scripts
  ./MegaCli64 -CfgLdDel -L1 -a0
  ./MegaCli64 -CfgLdDel -L2 -a0
}

enable_JBOD() {
   cd /root/install_scripts
  ./MegaCli64 -AdpSetProp EnableJBOD 1 -a0
}


delete_raid5
enable_JBOD
