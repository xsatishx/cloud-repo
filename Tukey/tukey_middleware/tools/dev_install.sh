#!/bin/bash
#set -e
DEV=true

sudo mkdir -p /var/log/tukey
sudo chown -R $USER:$USER /var/log/tukey/
sudo apt-get update
sudo apt-get install -y python-virtualenv libpq-dev python-dev pkg-config libfuse-dev memcached swig libffi-dev

if $DEV; then
    sudo apt-get install -y postgresql-9.1 postgresql-server-dev-9.1
fi

virtualenv ../.venv
source ../.venv/bin/activate

cd ..
cp tukey_middleware/local_settings.py{.example,}
while ! python setup.py install; do :;done
cd -

sudo -u postgres psql -c "CREATE DATABASE federated_auth;"
sudo -u postgres psql -c "CREATE USER cloudgui with PASSWORD 'password';"
sudo -u postgres psql federated_auth < schema

sudo -u postgres psql -d federated_auth -a -f cloud_values.sql
sudo -u postgres psql -d federated_auth -a -f method_values.sql

if $DEV; then
    USERNAME=`curl http://tukey-meta-data:6666/modules/v0/sullivan/username`
    PASSWORD=`curl http://tukey-meta-data:6666/modules/v0/sullivan/password`
    echo -n "Enter your openid email address: "
    read EMAIL
    python create_tukey_user.py sullivan openid $EMAIL $USERNAME $PASSWORD
fi

# apache stuff
exit

sudo mkdir -p /var/www/tukey
sudo chown -R $USER:$USER /var/www/tukey/
cd /var/www/tukey/tukey-middleware


