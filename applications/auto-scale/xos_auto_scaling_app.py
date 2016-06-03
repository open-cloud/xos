import socket
import requests
import urllib2
import json
import msgpack
import collections
import time, thread, threading

from flask import request, Request, jsonify
from flask import Flask
from flask import make_response
app = Flask(__name__)

projects_map = {}
xos_tenant_info_map = {}
xos_instances_info_map = {}

use_kafka = True

XOS_ENDPOINT = '130.127.133.58:9999'
KAFKA_SERVER_IP = '130.127.133.58'
KAFKA_SERVER_PORT = '9092'
KAFKA_TOPIC = 'auto-scale'
LOCAL_KAFKA_TARGET_URL = 'kafka://'+KAFKA_SERVER_IP+':'+KAFKA_SERVER_PORT+'?topic='+KAFKA_TOPIC

if use_kafka:
   import kafka
   from kafka import TopicPartition
else:
   UDP_IP = "0.0.0.0"
   UDP_PORT = 12346

@app.route('/autoscaledata',methods=['GET'])
def autoscaledata():
    response = app.make_response(json.dumps(projects_map.values()))
    response.mimetype="application/json"
    return response

def acquire_xos_monitoring_channel():
    url = "http://"+XOS_ENDPOINT+"/api/tenant/ceilometer/monitoringchannel/"
    admin_auth=("padmin@vicci.org", "letmein")   # use your XOS username and password
    monitoring_channels = requests.get(url, auth=admin_auth).json()
    ceilometer_url = None
    if not monitoring_channels:
        print 'SRIKANTH: No monitoring channels for this user...'
        return None
    else:
        monitoring_channel = monitoring_channels[0]
    while not monitoring_channel['ceilometer_url']:
         print 'SRIKANTH: Waiting for monitoring channel create'
         sleep(0.5)
         monitoring_channel = requests.get(url, auth=admin_auth).json()[0]
    #TODO: Wait until URL is completely UP
    while True:
        print 'SRIKANTH: Waiting for ceilometer proxy URL %s is available' % monitoring_channel['ceilometer_url']
        try:
            response = urllib2.urlopen(monitoring_channel['ceilometer_url'],timeout=1)
            break
        except urllib2.HTTPError, e:
            print 'SRIKANTH: HTTP error %s' % e.reason
            break
        except urllib2.URLError, e:
            print 'SRIKANTH: URL error %s' % e.reason
            pass
    return monitoring_channel

def print_samples():
   print ""
   print ""
   for project in projects_map.keys():
        print "service=%s slice=%s, alarm_state=%s" % (projects_map[project]['service'], projects_map[project]['slice'] if projects_map[project]['slice'] else project, projects_map[project]['alarm'])
        for resource in projects_map[project]['resources'].keys():
             print "resource=%s" % (projects_map[project]['resources'][resource]['xos_instance_info']['instance_name'] if projects_map[project]['resources'][resource]['xos_instance_info'] else resource)
             for i in projects_map[project]['resources'][resource]['queue']:
                  print "    time=%s val=%s" % ( i['timestamp'],i['counter_volume'])

def periodic_print():
     print_samples()
     #Print every 1minute
     threading.Timer(20, periodic_print).start()


CPU_UPPER_THRESHOLD = 80 #80%
CPU_LOWER_THRESHOLD = 30 #30%
CPU_THRESHOLD_REPEAT = 3
INITIAL_STATE = 'normal_config'
SCALE_UP_EVALUATION = 'scale_up_eval'
SCALE_DOWN_EVALUATION = 'scale_down_eval'
SCALE_UP_ALARM = 'scale_up'
SCALE_DOWN_ALARM = 'scale_down'

def loadAllXosTenantInfo():
    print "SRIKANTH: Loading all XOS tenant info"
    url = "http://"+XOS_ENDPOINT+"/xos/controllerslices/"
    admin_auth=("padmin@vicci.org", "letmein")   # use your XOS username and password
    controller_slices = requests.get(url, auth=admin_auth).json()
    for cslice in controller_slices:
         slice = requests.get(cslice['slice'], auth=admin_auth).json()
         slice_name = slice['humanReadableName']
         if slice['service']:
             service = requests.get(slice['service'], auth=admin_auth).json()
             service_name = service['humanReadableName']
         else:
             service_name = None
         xos_tenant_info_map[cslice['tenant_id']] = {'service':service_name, 'slice':slice_name}
         print "SRIKANTH: Project: %s Service:%s Slice:%s" % (cslice['tenant_id'],service_name,slice_name)

def loadAllXosInstanceInfo():
    print "SRIKANTH: Loading all XOS instance info"
    url = "http://"+XOS_ENDPOINT+"/xos/instances/"
    admin_auth=("padmin@vicci.org", "letmein")   # use your XOS username and password
    xos_instances = requests.get(url, auth=admin_auth).json()
    for instance in xos_instances:
         xos_instances_info_map[instance['instance_uuid']] = {'instance_name':instance['instance_name']}

def getXosTenantInfo(project):
    xos_tenant_info = xos_tenant_info_map.get(project, None)
    if xos_tenant_info:
        return xos_tenant_info
    else:
        loadAllXosTenantInfo()
        xos_tenant_info = xos_tenant_info_map.get(project, None)
        if not xos_tenant_info:
            print "SRIKANTH: Project %s has no associated XOS slice" % project
        return xos_tenant_info

def getXosInstanceInfo(resource):
    xos_instance_info = xos_instances_info_map.get(resource, None)
    if xos_instance_info:
        return xos_instance_info
    else:
        loadAllXosInstanceInfo()
        xos_instance_info = xos_instances_info_map.get(resource, None)
        if not xos_instance_info:
            print "SRIKANTH: Resource %s has no associated XOS instance" % project
        return xos_instance_info

def handle_adjust_scale(project, adjust):
    if (adjust != 'up') and (adjust != 'down'):
        print "SRIKANTH: Invalid adjust value %s " % adjust
        return
    current_instances = len(projects_map[project]['resources'].keys())
    if (current_instances <=1 and adjust == 'down'):
        print "SRIKANTH: %s is running with already minimum instances and can not scale down further " % project
        return
    if (current_instances >=2 and adjust == 'up'):
        print "SRIKANTH: %s is running with already maximum instances and can not scale up further " % project
        return
    #xos_tenant = getXosTenantInfo(project)
    xos_service = projects_map[project]['service']
    xos_slice = projects_map[project]['slice']
    if not xos_service or not xos_slice: 
        print "SRIKANTH: Can not handle adjust_scale for Project %s because not associated with any service or slice" % project
        return
    print "SRIKANTH: SCALE %s for Project %s, Slice=%s, Service=%s from current=%d to new=%d" % (adjust, project, xos_slice, xos_service, current_instances, current_instances+1 if (adjust=='up') else current_instances-1)
    query_params = {'service':xos_service, 'slice_hint':xos_slice, 'scale':current_instances+1 if (adjust=='up') else current_instances-1}
    url = "http://"+XOS_ENDPOINT+"/xoslib/serviceadjustscale/"
    admin_auth=("padmin@vicci.org", "letmein")   # use your XOS username and password
    response = requests.get(url, params=query_params, auth=admin_auth).json()
    print "SRIKANTH: XOS adjust_scale response: %s" % response

def periodic_cpu_threshold_evaluator():
     for project in projects_map.keys():
          aggregate_cpu_util = sum([resource['queue'][-1]['counter_volume'] \
                                     for resource in projects_map[project]['resources'].values()]) \
                                     /len(projects_map[project]['resources'].keys())

          if (projects_map[project]['alarm'] == INITIAL_STATE or
              projects_map[project]['alarm'] == SCALE_UP_ALARM or
              projects_map[project]['alarm'] == SCALE_DOWN_ALARM):
              if aggregate_cpu_util > CPU_UPPER_THRESHOLD:
                  projects_map[project]['uthreadshold_count'] = 1
                  projects_map[project]['alarm'] = SCALE_UP_EVALUATION
                  if projects_map[project]['uthreadshold_count'] >= CPU_THRESHOLD_REPEAT:
                      projects_map[project]['alarm'] = SCALE_UP_ALARM
                      handle_adjust_scale(project, 'up')
              elif aggregate_cpu_util < CPU_LOWER_THRESHOLD:
                  projects_map[project]['lthreadshold_count'] = 1
                  projects_map[project]['alarm'] = SCALE_DOWN_EVALUATION
                  if projects_map[project]['lthreadshold_count'] >= CPU_THRESHOLD_REPEAT:
                      projects_map[project]['alarm'] = SCALE_DOWN_ALARM
                      handle_adjust_scale(project, 'down')
              else:
                  projects_map[project]['uthreadshold_count'] = 0
                  projects_map[project]['lthreadshold_count'] = 0
                  projects_map[project]['alarm'] = INITIAL_STATE
          elif projects_map[project]['alarm'] == SCALE_UP_EVALUATION:
              if aggregate_cpu_util > CPU_UPPER_THRESHOLD:
                  projects_map[project]['uthreadshold_count'] += 1
                  if projects_map[project]['uthreadshold_count'] >= CPU_THRESHOLD_REPEAT:
                      projects_map[project]['alarm'] = SCALE_UP_ALARM
                      handle_adjust_scale(project, 'up')
              elif aggregate_cpu_util < CPU_LOWER_THRESHOLD:
                  projects_map[project]['lthreadshold_count'] += 1
                  projects_map[project]['alarm'] = SCALE_DOWN_EVALUATION
              else:
                  projects_map[project]['uthreadshold_count'] = 0
                  projects_map[project]['alarm'] = INITIAL_STATE
          elif projects_map[project]['alarm'] == SCALE_DOWN_EVALUATION:
              if aggregate_cpu_util < CPU_LOWER_THRESHOLD:
                  projects_map[project]['lthreadshold_count'] += 1
                  if projects_map[project]['lthreadshold_count'] >= CPU_THRESHOLD_REPEAT:
                      projects_map[project]['alarm'] = SCALE_DOWN_ALARM
                      handle_adjust_scale(project, 'down')
              elif aggregate_cpu_util > CPU_UPPER_THRESHOLD:
                  projects_map[project]['uthreadshold_count'] += 1
                  projects_map[project]['alarm'] = SCALE_UP_EVALUATION
              else:
                  projects_map[project]['lthreadshold_count'] = 0
                  projects_map[project]['alarm'] = INITIAL_STATE
     threading.Timer(20, periodic_cpu_threshold_evaluator).start()

def read_notification_from_ceilometer_over_kafka(host,port,topic):
    print "Kafka target" , host, port, topic
    try :
        consumer=kafka.KafkaConsumer(bootstrap_servers=["%s:%s" % (host,port)])
        consumer.assign([TopicPartition(topic,0)])
        consumer.seek_to_end()
        for message in consumer:
            #print message.value
            #logging.debug("%s",message.value)
            process_notification_from_ceilometer(json.loads(message.value))
            #status = process_ceilometer_message(json.loads(message.value),message.value)
            #print status
    except Exception as e:
        print "AUTO_SCALE Exception:",e

def read_notification_from_ceilometer(host,port):
   udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
   udp.bind((host, port))

   while True:
      data, source = udp.recvfrom(64000)
      try:
         sample = msgpack.loads(data, encoding='utf-8')
         process_notification_from_ceilometer(sample)
      except Exception as e:
         print e

def process_notification_from_ceilometer(sample):
         if sample['counter_name'] == 'instance':
             if ('event_type' in sample['resource_metadata'].keys()) and ('delete' in sample['resource_metadata']['event_type']):
	          xosTenantInfo = getXosTenantInfo(sample['project_id'])
                  xosResourceInfo = getXosInstanceInfo(sample['resource_id'])
                  print "SRIKANTH: Project %s Instance %s is getting deleted" % (xosTenantInfo['slice'] if xosTenantInfo['slice'] else sample['project_id'],xosResourceInfo) 
                  if sample['project_id'] not in projects_map.keys():
                       return
                  if sample['resource_id'] not in projects_map[sample['project_id']]['resources'].keys():
                       return
                  projects_map[sample['project_id']]['resources'].pop(sample['resource_id'], None)
             return
         elif sample['counter_name'] != 'cpu_util':
              return
         if sample['project_id'] not in projects_map.keys():
              projects_map[sample['project_id']] = {}
	      xosTenantInfo = getXosTenantInfo(sample['project_id'])
              projects_map[sample['project_id']]['project_id'] = sample['project_id']
              projects_map[sample['project_id']]['slice'] = xosTenantInfo['slice']
              projects_map[sample['project_id']]['service'] = xosTenantInfo['service']
              projects_map[sample['project_id']]['resources'] = {}
              projects_map[sample['project_id']]['uthreadshold_count'] = 0
              projects_map[sample['project_id']]['lthreadshold_count'] = 0
              projects_map[sample['project_id']]['alarm'] = INITIAL_STATE
         resource_map = projects_map[sample['project_id']]['resources']
         if sample['resource_id'] not in resource_map.keys():
              resource_map[sample['resource_id']] = {}
              resource_map[sample['resource_id']]['xos_instance_info'] = getXosInstanceInfo(sample['resource_id'])
              resource_map[sample['resource_id']]['queue'] = []
         samples_queue = resource_map[sample['resource_id']]['queue']
         sample = {'counter_name':sample['counter_name'],
                   'project_id':sample['project_id'],
                   'resource_id':sample['resource_id'],
                   'timestamp':sample['timestamp'],
                   'counter_unit':sample['counter_unit'],
                   'counter_volume':sample['counter_volume']}
         deque = collections.deque(samples_queue, maxlen=10)
         deque.append(sample)
         resource_map[sample['resource_id']]['queue'] = list(deque)

def setup_webserver():
    try:
        #config = ConfigParser.ConfigParser()
        #config.read('pub_sub.conf')
        #webserver_host = config.get('WEB_SERVER','webserver_host')
        #webserver_port = int (config.get('WEB_SERVER','webserver_port'))
        #client_host    = config.get('CLIENT','client_host')
        #client_port    = int (config.get('CLIENT','client_port'))
 
        #log_level    = config.get('LOGGING','level')
        #log_file       = config.get('LOGGING','filename')
   
        #level = LEVELS.get(log_level, logging.NOTSET) 
        #logging.basicConfig(filename=log_file,format='%(asctime)s %(levelname)s %(message)s',\
        #            datefmt=_DEFAULT_LOG_DATE_FORMAT,level=level) 
        webserver_host = '0.0.0.0'
        webserver_port = 9991
   
    except Exception as e:
        print("* Error in config file:",e.__str__())
        logging.error("* Error in confing file:%s",e.__str__())
    else: 
        app.run(host=webserver_host,port=webserver_port,debug=True, use_reloader=False)


def main():
   monitoring_channel = acquire_xos_monitoring_channel()
   if not monitoring_channel:
        print 'SRIKANTH: XOS monitoring_channel is not created... Create it before using this app'
        return
   loadAllXosTenantInfo()
   loadAllXosInstanceInfo()
   ceilometer_url = monitoring_channel['ceilometer_url']
   if use_kafka:
       thread.start_new(read_notification_from_ceilometer_over_kafka, (KAFKA_SERVER_IP,KAFKA_SERVER_PORT,KAFKA_TOPIC,))
       subscribe_data = {"sub_info":"cpu_util","app_id":"xos_auto_scale","target":LOCAL_KAFKA_TARGET_URL}
   else:
       thread.start_new(read_notification_from_ceilometer,(UDP_IP,UDP_PORT,))
       subscribe_data = {"sub_info":"cpu_util","app_id":"xos_auto_scale","target":"udp://10.11.10.1:12346"}
   subscribe_url = ceilometer_url + 'v2/subscribe'
   response = requests.post(subscribe_url, data=json.dumps(subscribe_data))
   print 'SRIKANTH: Ceilometer meter "cpu_util" Subscription status:%s' % response.text
   #TODO: Fix the typo in 'sucess'
   if (not 'sucess' in response.text) and (not 'already exists' in response.text):
       print 'SRIKANTH: Ceilometer meter "cpu_util" Subscription unsuccessful...Exiting'
       return
   if use_kafka:
        subscribe_data = {"sub_info":"instance","app_id":"xos_auto_scale2","target":LOCAL_KAFKA_TARGET_URL}
   else:
        subscribe_data = {"sub_info":"instance","app_id":"xos_auto_scale2","target":"udp://10.11.10.1:12346"}
   subscribe_url = ceilometer_url + 'v2/subscribe'
   response = requests.post(subscribe_url, data=json.dumps(subscribe_data))
   print 'SRIKANTH: Ceilometer meter "instance" Subscription status:%s' % response.text
   #TODO: Fix the typo in 'sucess'
   if (not 'sucess' in response.text) and (not 'already exists' in response.text):
       print 'SRIKANTH: Ceilometer meter "instance"Subscription unsuccessful...Exiting'
       return
   periodic_cpu_threshold_evaluator()
   periodic_print()
   setup_webserver()

if __name__ == "__main__":
   main()
