#!/usr/bin/python3
from threading import Thread

from collections import namedtuple
import subprocess
import datetime, time
Profile = namedtuple("Profile", ['openid', 'N', 'E', 'cookiefl', 'status_string'])

class Profile:
    def __init__(self, openid, N, E):
        self.openid = openid
        self.N = N
        self.E = E
        self.cookiefl = '/tmp/tm.profile.'+openid
        self.status_string = 'Launched at ' + str(datetime.datetime.now())

profiles = []
# You must only append/read the list in http thread.
# You must only operating on list.data in teachermate thread.

def teachermate_daemon():
    global profiles
    while True:
        for prof in profiles:
            if prof.cookiefl == '':
                continue
            # subprocess.call is outdated. Now I'm using everything in docker so I won't support python<3.5 anymore
            # ret = subprocess.call(['./signin-once.fish', prof.openid, prof.N, prof.E, prof.cookiefl])
            completed = subprocess.run(['./signin-once.fish', prof.openid, prof.N, prof.E, prof.cookiefl], stdout=subprocess.PIPE)
            ret = completed.return_code
            if ret == 0:
                stdout = completed.stdout.decode('utf-8').strip()
                def findStudentRankFromStdout(s):
                    # {"signRank":34,"studentRank":1}
                    pos = s.find('studentRank')
                    return -1 if pos == -1 else int(s[pos+13:-1])
                prof.status_string += '\nSuccessed at {}, You\'re the {}th student to signin!'.format(str(datetime.datetime.now()), findStudentRankFromStdout(stdout)) 
            elif ret == 1:
                prof.status_string += '\nFailed to signin at ' + str(datetime.datetime.now())
            elif ret == 2:
                prof.status_string += '\nOpenID is expired at ' + str(datetime.datetime.now())
                prof.cookiefl = ''
        time.sleep(15)

import http.server, socketserver
from urllib.parse import urlparse, parse_qs
import verify

import sys

try:
    listen_port = int(sys.argv[1])
except:
    listen_port = 25503

class my_handler(http.server.BaseHTTPRequestHandler):
    def query_task(self, openid):
        global profiles
        for prof in profiles:
            if prof.openid == openid:
                return "Task {} at {}N, {}E: \r\n{}".format(prof.openid, prof.N, prof.E, prof.status_string)
        return 'Task {} not found'.format(openid)
    def query_all(self):
        global profiles
        res = ''
        for prof in profiles:
            res += "\r\nTask {} at {}N, {}E: \r\n{}".format(prof.openid, prof.N, prof.E, prof.status_string)
        return res
    def get_index(self):
        with open('./index.html') as f:
            return f.read()
    def process(self):
        global profiles
        if self.path.startswith('/addtask'):
            args = parse_qs(urlparse(self.path).query)
            if not verify.verify_key(args['key'][0]):
                return 'invalid key'
            new_prof = Profile(args['openid'][0], args['N'][0], args['E'][0])
            profiles.append(new_prof)
            return 'done'
        elif self.path.startswith('/querytask'):
            args = parse_qs(urlparse(self.path).query)
            return self.query_task(args['openid'][0])
        elif self.path.startswith('/queryall_recolic_96100821'):
            return self.query_all()
        else:
            return self.get_index()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
    def do_GET(self):
        global profiles
        try:
            resp = self.process().encode('utf-8')
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(resp)
        except KeyError:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write('invalid api usage.'.encode('utf-8'))

if __name__ == "__main__":
    thread = Thread(target = teachermate_daemon, args = [])
    thread.start()
    
    try:
        server = http.server.HTTPServer(('', listen_port), my_handler)
        print('Listening *:' + str(listen_port))
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
    
