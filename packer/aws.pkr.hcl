packer {
  required_plugins {
    amazon = {
      version = ">= 1.2.8"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", ""
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "subnet_id" {
  type    = string
  default = "subnet-0c2f9279233534c28"
}

variable "vpc_id" {
  type    = string
  default = "vpc-0b451a27b094aa7c2"
}

variable "aws_user" {
  type        = string
  default     = "888577037865"
  description = "Set to 'demo' to use the demo AWS account"
}

# Set the DEMO account ID
locals {
  demo_account_id = "888577037865"
}



source "amazon-ebs" "ubuntu" {
  region          = "${var.aws_region}"
  ami_name        = "app-packer_aws_${local.timestamp}"
  ami_description = "AMI for Flask App"
  instance_type   = "t2.micro"
  ami_regions     = ["us-east-1", ]
  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["099720109477"]
  }
  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }
  ssh_username = "${var.ssh_username}"
  subnet_id    = "${var.subnet_id}"
  vpc_id       = "${var.vpc_id}"
  ami_users    = ["${var.aws_user}"]

  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/sda1"
    volume_size           = 8
    volume_type           = "gp2"
  }
}

build {
  name = "app-aws-packer"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  provisioner "file" {
    source      = "/home/runner/work/webapp/webapp/webapp.zip"
    destination = "/tmp/webapp.zip"
  }

  # Copy the systemd service file to /etc/systemd/system/
  provisioner "file" {
    source      = "app.service"
    destination = "/tmp/app.service"
  }

  # Run the setup script for the app
  provisioner "shell" {
    script = "./app.sh"
  }
}
