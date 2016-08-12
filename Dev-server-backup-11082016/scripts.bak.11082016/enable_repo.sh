apt-get update && apt-get dist-upgrade -y
apt-get install software-properties-common
yes '' | add-apt-repository cloud-archive:liberty
apt-get update && apt-get dist-upgrade -y
