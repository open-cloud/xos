#! /usr/bin/env python

import json
import os
import requests
import sys
import traceback

def main():
    global opencloud_auth

    if len(sys.argv)!=5:
        print >> sys.stderr, "syntax: run_tosca.py <port> <username> <password> <fn>"
        sys.exit(-1)

    port = int(sys.argv[1])
    username = sys.argv[2]
    password = sys.argv[3]
    tosca_fn = sys.argv[4]

    xos_auth=(username, password)

    hostname = "127.0.0.1"
    url = "http://%s:%d/api/utility/tosca/run/" % (hostname, port)

    recipe = open(tosca_fn).read()

    r = requests.post(url, data={"recipe": recipe}, auth=xos_auth)
    if (r.status_code != 200):
        print >> sys.stderr, "ERR: recieved status %d" % r.status_code
        try:
            print >> sys.stderr, r.json()["error_text"]
        except:
            traceback.print_exc("error while printing the error!")
            print r.text
        sys.exit(-1)

    result = r.json()
    if "log_msgs" in result:
        print "\n".join(result["log_msgs"])+"\n"

if __name__ == "__main__":
    main()

