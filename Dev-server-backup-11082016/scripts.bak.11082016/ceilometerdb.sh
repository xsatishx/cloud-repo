mongo --host 10.0.2.13  --eval '
  db = db.getSiblingDB("ceilometer");
  db.addUser({user: "ceilometer",
  pwd: "healthseq",
  roles: [ "readWrite", "dbAdmin" ]})'
  
