#!/bin/bash
set -e

# Update the system package index
echo "Updating package index..."
sudo apt-get update -y

# Install necessary packages (Python, pip, MySQL, unzip) without prompts
echo "Installing Python, pip, MySQL, and unzip..."
sudo  apt-get install -y python3 python3-pip mysql-server unzip

# Install MariaDB (for this assignment)
sudo apt install mariadb-server -y
sudo apt-get install -y libmariadb-dev

# Create a new non-login user for the application
echo "Creating non-login user 'csye6225'..."
sudo useradd --system --no-create-home --shell /usr/sbin/nologin csye6225

# Set up MySQL user and privileges
echo "Setting up MySQL..."
sudo mariadb -e "CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin';"
sudo mariadb -e "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost';"
sudo mariadb -e "FLUSH PRIVILEGES;"

# Unzip the webapp.zip file into /tmp/webapp
echo "Extracting app to opt folder"
sudo unzip /tmp/webapp.zip -d /opt/

echo "****LS done below*******"
ls /opt/

# Change ownership of the webapp directory to the new user
echo "Setting ownership of application files..."
sudo chown -R csye6225:csye6225 /opt/webapp
sudo chmod -R 755 /opt/webapp

sudo mv /tmp/app.service /etc/systemd/system/app.service

# Create the .env file with environment variables
echo "Creating .env file for MySQL setup..."
# cat <<EOF > /opt/webapp/.env
sudo bash -c 'cat <<EOF > /opt/webapp/.env
DB_USERNAME=admin
DB_PASSWORD=admin
DB_NAME=test
DB_HOST=localhost
DB_PORT=3306
EOF'

sudo chown -R csye6225:csye6225 /opt/webapp/.env
sudo chmod -R 755 /opt/webapp/.env

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
sudo systemctl start app.service


