#!/bin/sh
# this script is used to run the application in Linux
while true; do
    flask db upgrade
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
gunicorn -b :5000 walter:app