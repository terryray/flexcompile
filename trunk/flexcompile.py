#!/usr/bin/env python

import getpass
import os
import re
import time
import socket
import subprocess
import sys

HOST = ""
PORT = 53000 + os.getuid()

def slurp_chunk(proc, conn):
    chunk = ""
    while True:
        l = proc.stdout.read(1)
        if l is None:
            break
        conn.send(l)
        chunk += l
        if chunk.endswith("\n(fcsh)"):
            return chunk

def daemon(debug=False):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    curdir = os.getcwd()
    cmd = ""
    proc = None
    prevcmds = {}
    while True:
        conn, addr = s.accept()
        data = conn.recv(1024)
        needkill = False
        for line in data.split(";"):
            line = line.strip()
            if debug: print "< %s" % line
            if line.startswith("cd "):
                d = line[3:].strip()
                if d != curdir:
                    curdir = d
                    needkill = True
            else:
                cmd = line
                if cmd in prevcmds:
                    cmd = "compile %d" % prevcmds[cmd]
        if not proc or needkill:
            if proc:
                proc.stdin.close()
                proc.wait()
            os.chdir(curdir)
            if debug: print "doing popen"
            proc = subprocess.Popen(("/usr/local/flex/bin/fcsh",),
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            chunk = slurp_chunk(proc, conn)

        if debug: print "writing %s" % cmd
        proc.stdin.write(cmd + "\n")
        proc.stdin.flush()
        chunk = slurp_chunk(proc, conn)
        if cmd not in prevcmds:
            match = re.search(r'fcsh: Assigned (\d+) as the compile target id',
                              chunk)
            if match:
                prevcmds[cmd] = int(match.group(1))
        conn.send("\nDone\n")
        conn.close()
        if debug: print "closed connection"


def sendit(cmd, start_daemon_if_missing=True):
    cmd = "cd %s ; %s" % (os.getcwd(), cmd)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except socket.error:
        if not start_daemon_if_missing:
            print "No daemon process; running directly."
            os.system(cmd)
            return
        print "No daemon process, creating one..."
        os.system("%s -daemon &" % sys.argv[0])
        time.sleep(2)
        return sendit(cmd, start_daemon_if_missing=False)
    s.send(cmd)
    result = ""
    while True:
        data = s.recv(10240)
        sys.stdout.write(data)
        sys.stdout.flush()
        result += data
        if result.endswith("\nDone\n"):
            break
    print "All done."
        



# import pdb ; pdb.set_trace()
if sys.argv[1] == "-daemon":
    daemon()
else:
    cmd = ' '.join(sys.argv[1:])
    if getpass.getuser() in ['release', 'root']:
        os.system(cmd)
    else:
        sendit(cmd)
                                    
                
