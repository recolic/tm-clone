#!/bin/bash

cd .. &&
tar -cvzf teachermate-seller.tar.gz teachermate-seller/ &&
scp teachermate-seller.tar.gz root@mc.recolic.net:~/ &&
ssh root@mc.recolic.net 'bash -c "cd /var/www && mv ~/teachermate-seller.tar.gz . && rm -rf teachermate-seller && tar -xvzf teachermate-seller.tar.gz && systemctl restart tm"'

