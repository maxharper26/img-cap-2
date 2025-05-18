#!/bin/bash

sudo yum install python3-pip -y
pip install flask
pip install mysql-connector-python
pip install boto3 werkzeug
sudo yum install -y mariadb105
sudo yum install -y git
git clone https://github.com/maxharper26/img-cap-2.git
cd img-cap-2
python3 app.py