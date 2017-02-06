#!/bin/bash

sudo apt-get install python python-dev python-pip libpq-dev postgresql postgresql-contrib
sudo pip2 install virtualenv django psycopg2
python databases.py
source ~/.django/bin/activate

