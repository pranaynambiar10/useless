#!/bin/bash
# This script starts the application servers.
# It is run as ec2-user.

cd /home/ec2-user/meme-alchemist

# Start the backend server
cd backend
# source venv/bin/activate # If you use a virtual environment
uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
cd ..

# Start the frontend server
cd frontend
npm run dev > /dev/null 2>&1 &

echo "Servers started."
