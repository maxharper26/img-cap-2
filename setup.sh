#!/bin/bash

# Update package list
sudo apt-get update

# Install Python3 and Git
sudo apt-get install -y python3 python3-pip git

# Clone the repository (replace with your actual repo URL)
git clone https://github.com/yourusername/your-repo-name.git

# Enter the repo directory
cd your-repo-name

# Install Python dependencies
pip3 install -r requirements.txt

# Run the app (adjust if the app entry point is different)
python3 main.py