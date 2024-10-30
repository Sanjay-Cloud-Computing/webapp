#!/bin/bash
set -e

echo "Updating package index..."
sudo apt-get update -y

echo "Installing Python, pip, and unzip..."
sudo apt-get install -y python3 python3-pip unzip

echo "Creating non-login user 'csye6225'..."
sudo useradd --system --no-create-home --shell /usr/sbin/nologin csye6225

pwd

echo "Extracting app to /opt folder"
sudo unzip /tmp/webapp.zip -d /opt/

echo "**** Listing /opt contents ****"
ls /opt/
echo "inside webapp"
ls /opt/webapp/

pwd
ls -R /opt/
# ls -r /opt/
# ls /opt/webapp/packer
echo "Setting ownership of application files..."
sudo chown -R csye6225:csye6225 /opt/webapp
sudo chmod -R 755 /opt/webapp

# Move service file for the app
sudo mv /tmp/app.service /etc/systemd/system/app.service

# Install CloudWatch Agent by downloading directly from AWS
sudo apt-get update
curl -O https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# Move CloudWatch configuration
echo "Setting up CloudWatch Agent configuration..."

echo "**** Listing /opt contents ****"
# sudo chown -R csye6225:csye6225 /opt/webapp/packer
# sudo chmod -R 755 /opt/webapp/packer
ls /opt/
ls /opt/webapp/
ls /opt/webapp/app/controllers

sudo cp /opt/webapp/packer/amazon-cloudwatch-agent-config.json /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent-config.json

sudo chown -R csye6225:csye6225 /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent-config.json
sudo chmod -R 755 /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent-config.json

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent-config.json -s

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a start

# Setting up virtual environment for the app
echo "Setting up virtual environment..."
sudo apt-get install -y python3-venv
cd /opt/webapp

sudo pip install virtualenv
sudo virtualenv venv

sudo chown -R csye6225:csye6225 /opt/webapp/venv
sudo chmod -R 755 /opt/webapp/venv

source /opt/webapp/venv/bin/activate

# Install app dependencies
sudo pip install -r /opt/webapp/requirement.txt

# Start the app service
sudo systemctl daemon-reload
sudo systemctl enable app.service
