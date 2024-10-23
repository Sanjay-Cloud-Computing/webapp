#!/bin/bash
set -e

echo "Updating package index..."
sudo apt-get update -y

echo "Installing Python, pip, and unzip..."
sudo apt-get install -y python3 python3-pip unzip

echo "Creating non-login user 'csye6225'..."
sudo useradd --system --no-create-home --shell /usr/sbin/nologin csye6225

echo "Extracting app to opt folder"
sudo unzip /tmp/webapp.zip -d /opt/

echo "****LS done below*******"
ls /opt/

echo "Setting ownership of application files..."
sudo chown -R csye6225:csye6225 /opt/webapp
sudo chmod -R 755 /opt/webapp

sudo mv /tmp/app.service /etc/systemd/system/app.service

echo "Setting up virtual environment..."
sudo apt-get install -y python3-venv

cd /opt/webapp

sudo pip install virtualenv
sudo virtualenv venv

sudo chown -R csye6225:csye6225 /opt/webapp/venv
sudo chmod -R 755 /opt/webapp/venv

source /opt/webapp/venv/bin/activate

sudo pip install -r /opt/webapp/requirement.txt

sudo systemctl daemon-reload
sudo systemctl enable app.service