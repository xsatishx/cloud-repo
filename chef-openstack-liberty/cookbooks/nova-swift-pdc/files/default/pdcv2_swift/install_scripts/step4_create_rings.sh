#!/bin/bash

#SERVER_NAME=$(ip addr | grep inet | perl -ne 'm|(10.16.64.\d+)| && print "$1\n"')
#ZONE=$(echo $SERVER_NAME |  perl -ne 'm|10.16.64.(\d+)| && print "$1\n"')
SERVER_NAME=${1}
if [ "$SERVER_NAME" == "" ]
then
  echo "usage: $0 ServerName"
  exit 1
fi
ZONE=$(dig $SERVER_NAME +short |  perl -ne 'm|10.16.64.(\d+)| && print "$1\n"')

REGION=1
WEIGHT=100

NODEPATH=/srv/node/

# X Y Z where 2^X=Number of Total Drives in Ring*100 rounded up to nearest power of 2 ,  Y = replica count, Z = max xfer of replica in hours::
POWER=16
REPN=3
REPHRS=1




set_node_perms() {
        #Set the Nodes permissions or swift can not write to it.
        chown swift:swift /srv/node/* -R
        chmod 770 /srv/node/* -R
}


init_ring() {
  #Swift needs this file at /etc/swift for each ring to say it exists
  RING=${1}
  cd /etc/swift
      swift-ring-builder ${RING}.builder create $POWER $REPN $REPHRS
}


mk_ring() {
  #This adds a drive to the swift rings.  NEed tocopy this to all nodes for swift_proxy to work.

  RING=${1}
  cd /etc/swift
  case $RING in
    "account")
      PORT=6002
      RPORT=6005
    ;;
    "container")
      PORT=6001
      RPORT=6004
    ;;
    "object")
      PORT=6000
      RPORT=6003
    ;;

    *)
      echo "Func Usage mk_ring account|container|object drvpath"
      exit 1
    ;;
  esac

  for drvpath in $(cd $NODEPATH; ls )
  do
    swift-ring-builder ${RING}.builder add --zone ${ZONE} --ip ${SERVER_NAME}  --port $PORT --device $drvpath  --replication-ip ${SERVER_NAME} --replication-port $RPORT --weight $WEIGHT --region $REGION
  done

}


verify_ring() {
  RING=${1}
  cd /etc/swift
  swift-ring-builder ${RING}.builder
}

rebalance_ring() {
  RING=${1}
  cd /etc/swift
  swift-ring-builder ${RING}.builder rebalance
}


[ -e /etc/swift/account.builder ] ||   init_ring account
[ -e /etc/swift/container.builder ] ||  init_ring container
[ -e /etc/swift/object.builder ] ||  init_ring object

set_node_perms

mk_ring account
mk_ring container
mk_ring object

verify_ring account
verify_ring container
verify_ring object

rebalance_ring account
rebalance_ring container
rebalance_ring object

chown -R swift:swift /etc/swift


#now copy the *.builder and the .gz files to all nodes!
