#!/usr/bin/python
import socket,thread
import sys
import fnmatch
import operator
import logging
import ConfigParser
from urlparse import urlparse
from sflow_sub_records import *

from flask import request, Request, jsonify
from flask import Flask
from flask import make_response
app = Flask(__name__)

COMPARATORS = {
    'gt': operator.gt,
    'lt': operator.lt,
    'ge': operator.ge,
    'le': operator.le,
    'eq': operator.eq,
    'ne': operator.ne,
}

LEVELS = {'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}

_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

@app.route('/subscribe',methods=['POST'])
def subscribe():
    logging.debug(" SUB data:%s",request.data)
    target = request.data
    parse_target=urlparse(target)
    if not parse_target.netloc:
        err_str = "Error:Invalid target format"
        logging.error("* Invalid target format")
        return err_str 

    status = "" 
    if parse_target.scheme == "udp" :
         host=parse_target.hostname
         port=parse_target.port
         scheme = parse_target.scheme
         app_ip = host 
         app_port = port
 
         if host == None or port == None :
             err_str = "* Error: Invalid IP Address format"
             logging.error("* Invalid IP Address format")
             return err_str
  
         subscrip_obj=sflow_sub_record(scheme,None,app_ip,app_port,None,None)
         status = add_sflow_sub_record(subscrip_obj)
         print_sflow_sub_records()

    if parse_target.scheme == "kafka" :
         pass
    if parse_target.scheme == "file" :
         pass
    return status 

@app.route('/unsubscribe',methods=['POST'])
def unsubscribe():
    try :  
        target = request.data
        parse_target=urlparse(target)
        if not parse_target.netloc:
            err_str = "Error:Invalid target format"
            logging.error("* Invalid target format")
            return err_str 

        status = "" 
        if parse_target.scheme == "udp" :
            host=parse_target.hostname
            port=parse_target.port
            scheme = parse_target.scheme
            app_ip = host 
            app_port = port
 
            delete_sflow_sub_record(app_ip, app_port)
    except Exception as e:
         logging.error("* %s",e.__str__())
         return e.__str__()
    return "UnSubscrition is sucessful! \n"

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def sflow_recv(host,port):
   udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
   udp.bind((host, port))
   logging.info("Started sflow receive thread on %s:%s",host, str(port))

   while True:
      data, source = udp.recvfrom(64000)
      for obj in sflow_sub_database:
         target_host = obj.ipaddress
         target_port = int(obj.portno)
         try:  
             logging.debug("Replicating the sFlow data to:%s:%s",target_host, str(target_port))
             udp.sendto(data,(target_host,target_port))
         except Exception:
             logging.error ("Unable to send sFlow data to target %s:%s ",target_host,str(target_port))
   logging.warn("Exiting sflow receive thread")

     
def initialize(host,port):
     thread.start_new(sflow_recv,(host,port,))
        
if __name__ == "__main__":

    try:
        config = ConfigParser.ConfigParser()
        config.read('sflow_pub_sub.conf')
        webserver_host = config.get('WEB_SERVER','webserver_host')
        webserver_port = int (config.get('WEB_SERVER','webserver_port'))
        sflow_listening_ip_addr  = config.get('SFLOW','listening_ip_addr')
        sflow_listening_port  = int (config.get('SFLOW','listening_port'))

        log_level    = config.get('LOGGING','level')
        log_file       = config.get('LOGGING','filename')
   
        level = LEVELS.get(log_level, logging.NOTSET) 
        logging.basicConfig(filename=log_file,format='%(asctime)s %(levelname)s %(message)s',\
                    datefmt=_DEFAULT_LOG_DATE_FORMAT,level=level) 
    except Exception as e:
        print("* Error in config file:",e.__str__())
        logging.error("* Error in confing file:%s",e.__str__())
    else: 
        initialize(sflow_listening_ip_addr,sflow_listening_port)
        app.run(host=webserver_host,port=webserver_port,debug=False)
