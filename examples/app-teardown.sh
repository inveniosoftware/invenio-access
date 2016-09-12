#!/bin/sh

DIR=`dirname "$0"`

cd $DIR
export FLASK_APP=app.py

# Destroy the database
flask db destroy --yes-i-know

# clean environment
[ -e "$DIR/instance" ] && rm $DIR/instance -Rf
