
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/usr/bin/python

import copy
import json
from flask import Flask, make_response, request
from flask.ext.cors import CORS
from subprocess import call

app = Flask(__name__)
app.debug = True
CORS(app)

e_lines = {}


@app.route('/SCA_ETH_FDFr_EC/findByState', methods=['GET'])
def get_elines_by_state():
    resp = make_response(json.dumps(e_lines.values()))
    resp.mimetype = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/SCA_ETH_FDFr_EC', methods=['GET'])
def get_elines():
    resp = make_response(json.dumps(e_lines.values()))
    resp.mimetype = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/SCA_ETH_FDFr_EC/<name>/', methods=['GET'])
def get_eline(name):
    resp = make_response(json.dumps(e_lines[int(name)]))
    resp.mimetype = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# Convert long value to dotted hex value with specified length in bytes
def longToHex(l, length=6):
    h = ("%x" % l)
    if len(h) % 2 != 0:
        h = '0' + h
    result = ':'.join([h[i:i+2] for i in range(0, len(h), 2)])
    prefix = '00:' * (length - (len(h) / 2) - (len(h) % 2))
    return prefix + result


@app.route('/SCA_ETH_FDFr_EC', methods=['POST'])
def create_eline():
    # Store E-Line
    e_line = json.loads(request.data)
    e_line['id'] = len(e_lines) + 1

    e_lines[e_line['id']] = e_line

    # Create E-Line in ONOS
    flow_points = e_line['SCA_ETH_Flow_Points']

    # src_host = flow_points[0]['scaEthFppUniN']['transportPort']['Hostname'] + '/-' + flow_points[0]['scaEthFppUniN']['transportPort']['Port']
    # dst_host = flow_points[1]['scaEthFppUniN']['transportPort']['Hostname'] + '/-' + flow_points[1]['scaEthFppUniN']['transportPort']['Port']

    src_index = int(flow_points[0]['scaEthFppUniN']['transportPort']['Hostname'][-2:])
    dst_index = int(flow_points[1]['scaEthFppUniN']['transportPort']['Hostname'][-2:])

    src_host = str(longToHex(src_index, 6)) + '/-1'
    dst_host = str(longToHex(dst_index, 6)) + '/-1'

    print 'Creating E-Line between %s (%s) and %s (%s)' % (src_index, src_host, dst_index, dst_host)
    call(['onos', 'localhost', 'add-host-intent', src_host, dst_host])

    # Return response
    resp = make_response(json.dumps(e_line))
    resp.mimetype = 'application/json'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
