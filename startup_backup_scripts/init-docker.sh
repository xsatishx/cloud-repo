apt-get install apt-transport-https ca-certificates wget curl git -y
apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
touch /etc/apt/sources.list.d/docker.list
echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main"  > /etc/apt/sources.list.d/docker.list
apt-get install docker-engine -y --force-yes 

echo "Logging in"
docker login -u xsatishx -p xsatishx123

