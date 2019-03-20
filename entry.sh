#!/bin/bash

cd /var/www/teachermate-seller &&
unbuffer ./daemon.py >> log.log 2>&1
exit $?

