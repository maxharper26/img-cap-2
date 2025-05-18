#!/bin/bash

sudo yum install python3-pip -y
pip install flask
pip install mysql-connector-python
pip install boto3 werkzeug
sudo yum install -y mariadb105

sudo apt-get install -y git

# Clone the repository (replace with your actual repo URL)
git clone https://github.com/yourusername/your-repo-name.git

# Enter the repo directory
cd your-repo-name

# Install Python dependencies
pip3 install -r requirements.txt

# Run the app (adjust if the app entry point is different)
python3 main.py