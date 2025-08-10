#!/bin/bash
# Navigate to the application directory
cd /home/ec2-user/meme-alchemist

# Install frontend dependencies and build the frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Install backend dependencies
echo "Setting up backend..."
cd backend
# It's good practice to create and use a virtual environment
# python3 -m venv venv
# source venv/bin/activate
pip3 install -r requirements.txt

# (Optional) Add commands to start your application servers,
# possibly using a process manager like pm2 or systemd.
# For example:
# echo "Starting application servers..."
# pm2 start ecosystem.config.js
