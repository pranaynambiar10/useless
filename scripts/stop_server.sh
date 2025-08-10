#!/bin/bash
# This script stops the application servers.
# It is run as ec2-user.

# Example using pm2
# pm2 stop all
# pm2 delete all

# If you are running the servers directly, you might need to find and kill the processes.
# For example:
# pkill -f "uvicorn main:app"
# pkill -f "npm run dev"
echo "Servers stopped."
