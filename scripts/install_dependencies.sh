#!/bin/bash
# This script installs project dependencies.
# It is run as root before the application is installed.

# Update packages and install Node.js and npm
yum update -y
curl -sL https://rpm.nodesource.com/setup_16.x | bash -
yum install -y nodejs

# Install Python 3 and pip if they are not already installed
yum install -y python3-pip
