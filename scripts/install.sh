#!/bin/bash
cd /home/ec2-user/meme-alchemist
npm install
npm run build
cd backend
pip install -r requirements.txt
# Add any other backend setup commands here
