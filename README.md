# Project Setup & Deployment Guide

This document provides  instructions for setting up a development environment, deploying the web application to a remote server, configuring databases, and running the Flask application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Virtual Machine Configuration](#virtual-machine-configuration)
  - [Step 1: Establishing SSH Connection](#step-1-establishing-ssh-connection)
  - [Step 2: Transferring Files to the VM](#step-2-transferring-files-to-the-vm)
  - [Step 3: Configuring VM Storage](#step-3-configuring-vm-storage)
- [Database Setup](#database-setup)
  - [Installing Database Server](#installing-database-server)
  - [Configuring MySQL Database](#configuring-mysql-database)
- [Application Setup](#application-setup)
  - [Creating a Python Virtual Environment](#creating-a-python-virtual-environment)
  - [Installing Python Dependencies](#installing-python-dependencies)
- [Running the Application](#running-the-application)
- [Packer Integration](#packer-integration)
- [Continuous Integration (CI)](#continuous-integration)

## Prerequisites

Before setting up the environment, ensure the following tools and configurations are available:

- A Ubuntu-based virtual machine.
- SSH access configured with public and private keys.
- Administrative privileges on the VM.
- Required development packages for Python and MySQL.

---

## Virtual Machine Configuration

### Step 1: Establishing SSH Connection

1. Configure your SSH key and connect to your VM from your local machine:

    ```bash
    ssh root@your_vm_ip
    ```

2. Verify the connection before continuing

### Step 2: Transferring Files to the VM

1. **Upload the application source code** to the remote server using `scp`:

   ```bash
   scp -i ~/.ssh/your_ssh_key your_project.zip root@your_vm_ip:/root/
   ```

2. Unzip the transferred files on the remote server:

   ```bash
   unzip your_project.zip
   ```

### Step 3: Configuring VM Storage

1. Check the current storage and memory allocation:

   ```bash
    free -h
    ```

2. Add swap memory if required:

    ```bash
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    ```

3. Persist the swap configuration:

    ```bash
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    ```

## Database Setup

### Installing Database Server

1. Install MySQL:

```bash
sudo apt install mysql-server -y
```

2. Start the database service:

```bash
sudo systemctl start mysql
```

### Configuring MySQL Database

1. Log into the MySQL database:

```bash
sudo mysql -u root -p
```

2. Create a new database and user:

```bash
CREATE DATABASE my_database;
CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON my_database.* TO 'db_user'@'localhost';
FLUSH PRIVILEGES;
```

## Application Setup

### Creating a Python Virtual Environment

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Installing Python Dependencies

1. Install required Python packages:

```bash
pip install -r requirements.txt
```

### Running the Application

1. Run the Flask application:

```bash
python3 app.py
```

2. On VM Public:

```bash
flask run --host=0.0.0.0 --port=5000
```

3. Verify the application::

```bash
curl http://your_vm_ip:5000/
```

### Packer Integration

Packer is used to automate the creation of custom application images. These images will include all necessary application binaries, configurations, and databases. The images will be created and deployed via GitHub Actions.

### Continuous Integration

Set up automated testing using GitHub Action Workflows. Every time a pull request is created or updated, our CI workflow kicks in and runs all the tests to make sure everything is working as expected. If any tests fail, merging the pull request is blocked until the issues are fixed.

When a pull request is merged into the main branch, the packer_build workflow is triggered. This workflow uses Packer to build and deploy a custom image.

- **Automated Test Execution**: The workflow is configured to run tests on each pull request to ensure code meets quality standards.
- **Enforced Branch Rules**: Branch protection rules prevent merging if any tests fail, maintaining a reliable and stable codebase.

If you want to see the details, check out the `.github/workflows/app_check.yml` file.
