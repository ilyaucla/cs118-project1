#!/usr/bin/env python

from threading import Thread
from httplib import HTTPConnection
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from datetime import datetime, timedelta
#from bcolor import bcolors
import sys
import time
import re, socket, calendar
from datetime import datetime
from time import sleep

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    PASS = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class TestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/basic":
            lms = self.headers.get('If-Modified-Since', "")
            cdata = ""
            if lms != "":
                m_ts = datetime.strptime(lms, "%a, %d %b %Y %H:%M:%S GMT")
                c_ts = datetime.now()
                
                diff = c_ts - m_ts
                
                # this is a current version of the content
                if diff.seconds > 5 and diff.seconds < 10
                    lastModify=lms
                    expireDate=(datetime.now()+timedelta(seconds=5)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                    self.hit = True
                    self.send_response(304)
                    self.send_header('Expires',expireDate)
                    self.send_header('Last-Modified', lastModify)
                # give a new version of the content
                elif diff.seconds > 10:
                    cdata = "OK"
                    size = len(cdata)
                    expireDate=(datetime.now()+timedelta(seconds=5)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                    lastModify=(datetime.now()).strftime("%a, %d %b %Y %H:%M:%S GMT")
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.send_header('Content-length', str(size))
                    self.send_header('Expires',expireDate)
                    self.send_header('Last-Modified', lastModify)
                # content must be served from cache, it is wrong that you ask original server
                else:
                    cdata = "WRONG!\n"
                    size = len(cdata)
                    expireDate=(datetime.now()+timedelta(seconds=5)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                    lastModify=(datetime.now()).strftime("%a, %d %b %Y %H:%M:%S GMT")
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.send_header('Content-length', str(size))
                    self.send_header('Expires',expireDate)
                    self.send_header('Last-Modified', lastModify)

            else:
                cdata = open("./basic", "r").read()
                size = len(cdata)
                expireDate=(datetime.now()+timedelta(seconds=5)).strftime("%a, %d %b %Y %H:%M:%S GMT")
                lastModify=(datetime.now()).strftime("%a, %d %b %Y %H:%M:%S GMT")
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.send_header('Content-length', str(size))
                self.send_header('Expires',expireDate)
                self.send_header('Last-Modified', lastModify)

            if self.close_connection == True:
                self.send_header('Connection', 'close')
            self.end_headers()
            if cdata != "":
                self.wfile.write(cdata)

        return


class ServerThread (Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.port = port

    def run(self):
        try:
            TestHandler.protocol_version = "HTTP/1.1"
            TestHandler.hit = False
            self.server = HTTPServer(('', self.port), TestHandler)
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.server.socket.close() 


try:
    conf = open("./portconf", "r")
    pport  = conf.readline().rstrip().split(':')[1]
    sport1 = conf.readline().rstrip().split(':')[1]
    sport2 = conf.readline().rstrip().split(':')[1]
    server1 = ServerThread(int(sport1))
    server1.start()
    dataFile = open('basic', "r")
    cdata = dataFile.read()
    r = False
    proxy = '127.0.0.1:'+pport
    
    conn = HTTPConnection(proxy)
    conn.request("GET", "http://127.0.0.1:" + sport1 + "/basic")
    resp = conn.getresponse()
    data = resp.read()
    conn.close()

    time.sleep(3)
    conn2 = HTTPConnection(proxy)
    conn2.request("GET", "http://127.0.0.1:" + sport1 + "/basic")
    resp2 = conn2.getresponse()
    data2 = resp2.read()
    conn2.close()

    time.sleep(3)
    conn3 = HTTPConnection(proxy)
    conn3.request("GET", "http://127.0.0.1:" + sport1 + "/basic")
    resp3 = conn3.getresponse()
    data3 = resp3.read()
    conn3.close()

    time.sleep(6)
    conn4 = HTTPConnection(proxy)
    conn4.request("GET", "http://127.0.0.1:" + sport1 + "/basic")
    resp4 = conn4.getresponse()
    data4 = resp4.read()
    conn4.close()


    if data4 == "OK" and data3 == cdata and data2 == cdata:
        r = True
    if r:
        print "Re-query Caching: [" + bcolors.PASS + "PASSED" + bcolors.ENDC + "]"
    else:
        print "Re-query Caching: [" + bcolors.FAIL + "FAILED" + bcolors.ENDC + "]"
except:
    server1.server.shutdown()

server1.server.shutdown()

