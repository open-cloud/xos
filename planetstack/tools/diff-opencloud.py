#! /usr/bin/python

import base64
import os
import sys
import subprocess
import StringIO

if len(sys.argv)<3:
    print >> sys.stderr, "syntax: diff-opencloud <localfn> <remotehost:remotefn>"
    sys.exit(-1)

srcfn = sys.argv[1]
dest = sys.argv[2]

if not ":" in dest:
    print >> sys.stderr, "malformed desthost:destfn"
    sys.exit(-1)

(hostname,destfn) = dest.split(":",1)

if destfn.endswith("/"):
    destfn = destfn + os.path.basename(srcfn)

script = 'echo START; base64 %s' % destfn

file("/tmp/script","w").write(script)

p = subprocess.Popen(["ssh", "-A", hostname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
enctext = p.communicate(input=script)[0]

enctext = enctext.split("START")[1]

text = base64.b64decode(enctext)

file("/tmp/diff-src","w").write(text)
os.system("diff /tmp/diff-src %s" % srcfn)

"""
SRCPATHNAME=$1
DESTHOSTNAME=$2
DESTPATHNAME=$3
echo "base64 -d -i > $DESTPATHNAME <<EOF" > /tmp/ssh-up            
base64 $SRCPATHNAME >> /tmp/ssh-up   
echo "EOF" >> /tmp/ssh-up
ssh -A $DESTHOSTNAME < /tmp/ssh-up  
"""
