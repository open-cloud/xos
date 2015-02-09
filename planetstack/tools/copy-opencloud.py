#! /usr/bin/env python

import base64
import os
import sys
import subprocess
import StringIO

if len(sys.argv)<3:
    print >> sys.stderr, "syntax: copy-opencloud <srcfn> <desthost:destfn>"
    sys.exit(-1)

srcfn = sys.argv[1]
dest = sys.argv[2]

if not ":" in dest:
    print >> sys.stderr, "malformed desthost:destfn"
    sys.exit(-1)

(hostname,destfn) = dest.split(":",1)

if destfn.endswith("/"):
    destfn = destfn + os.path.basename(srcfn)

enctext = base64.b64encode(open(srcfn).read())
#script = 'sudo bash -C "base64 -d -i > %s <<EOF\n%s\nEOF\n"' % (destfn, enctext)
script = 'base64 -d -i > %s <<EOF\n%s\nEOF\n' % (destfn, enctext) 


file("/tmp/script","w").write(script)

p = subprocess.Popen(["ssh", "-A", hostname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print p.communicate(input=script)[0]


"""
SRCPATHNAME=$1
DESTHOSTNAME=$2
DESTPATHNAME=$3
echo "base64 -d -i > $DESTPATHNAME <<EOF" > /tmp/ssh-up            
base64 $SRCPATHNAME >> /tmp/ssh-up   
echo "EOF" >> /tmp/ssh-up
ssh -A $DESTHOSTNAME < /tmp/ssh-up  
"""
