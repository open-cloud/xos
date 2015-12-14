import socket
import requests
import urllib2
import json
import msgpack
import collections
import time, thread, threading

projects_map = {}
xos_tenant_info_map = {}
xos_instances_info_map = {}

UDP_IP = "0.0.0.0"
UDP_PORT = 12346

def acquire_xos_monitoring_channel():
    url = "http://ctl:9999/xoslib/monitoringchannel/"
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
            print 'SRIKANTH: URL error %(reason)s' % e.reason
            pass
    return monitoring_channel

def print_samples():
   print ""
   print ""
   for project in projects_map.keys():
        print "service=%s slice=%s, alarm_state=%s" % (projects_map[project]['xos_tenant_info']['service'] if projects_map[project]['xos_tenant_info'] else None, projects_map[project]['xos_tenant_info']['slice'] if projects_map[project]['xos_tenant_info'] else project, projects_map[project]['alarm'])
        for resource in projects_map[project]['resources'].keys():
             print "resource=%s" % (projects_map[project]['resources'][resource]['xos_instance_info']['instance_name'] if projects_map[project]['resources'][resource]['xos_instance_info'] else resource)
             for i in projects_map[project]['resources'][resource]['queue']:
                  print "    time=%s val=%s" % ( i['timestamp'],i['counter_volume'])

def periodic_print():
     print_samples()
     #Print every 1minute
     threading.Timer(60, periodic_print).start()


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
    url = "http://ctl:9999/xos/controllerslices/"
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
    url = "http://130.127.133.87:9999/xos/instances/"
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
    xos_tenant = projects_map[project]['xos_tenant_info']
    if not xos_tenant:
        print "SRIKANTH: Can not handle adjust_scale for Project %s because not associated with any slice" % project
        return
    xos_service = xos_tenant['service']
    xos_slice = xos_tenant['slice']
    if not xos_service or not xos_slice: 
        print "SRIKANTH: Can not handle adjust_scale for Project %s because not associated with any service or slice" % project
        return
    print "SRIKANTH: SCALE %s for Project %s, Slice=%s, Service=%s from current=%d to new=%d" % (adjust, project, xos_slice, xos_service, current_instances, current_instances+1 if (adjust=='up') else current_instances-1)
    query_params = {'service':xos_service, 'slice_hint':xos_slice, 'scale':current_instances+1 if (adjust=='up') else current_instances-1}
    url = "http://ctl:9999/xoslib/serviceadjustscale/"
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
     threading.Timer(60, periodic_cpu_threshold_evaluator).start()

def read_notification_from_ceilometer(host,port):
   udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
   udp.bind((host, port))

   while True:
      data, source = udp.recvfrom(64000)
      try:
         sample = msgpack.loads(data, encoding='utf-8')
         if sample['counter_name'] != 'cpu_util':
              continue
         if sample['project_id'] not in projects_map.keys():
              projects_map[sample['project_id']] = {}
              projects_map[sample['project_id']]['xos_tenant_info'] = getXosTenantInfo(sample['project_id'])
              projects_map[sample['project_id']]['resources'] = {}
              projects_map[sample['project_id']]['uthreadshold_count'] = 0
              projects_map[sample['project_id']]['lthreadshold_count'] = 0
              projects_map[sample['project_id']]['alarm'] = INITIAL_STATE
         resource_map = projects_map[sample['project_id']]['resources']
         if sample['resource_id'] not in resource_map.keys():
              resource_map[sample['resource_id']] = {}
              resource_map[sample['resource_id']]['xos_instance_info'] = getXosInstanceInfo(sample['resource_id'])
              resource_map[sample['resource_id']]['queue'] = collections.deque(maxlen=10)
         samples_map = resource_map[sample['resource_id']]['queue']
         sample = {'counter_name':sample['counter_name'],
                   'project_id':sample['project_id'],
                   'resource_id':sample['resource_id'],
                   'timestamp':sample['timestamp'],
                   'counter_unit':sample['counter_unit'],
                   'counter_volume':sample['counter_volume']}
         samples_map.append(sample)
      except Exception as e:
         print e

def main():
   monitoring_channel = acquire_xos_monitoring_channel()
   if not monitoring_channel:
        print 'SRIKANTH: XOS monitoring_channel is not created... Create it before using this app'
        return
   loadAllXosTenantInfo()
   loadAllXosInstanceInfo()
   thread.start_new(read_notification_from_ceilometer,(UDP_IP,UDP_PORT,))
   ceilometer_url = monitoring_channel['ceilometer_url']
   subscribe_data = {"sub_info":"cpu_util","app_id":"xos_auto_scale","target":"udp://10.11.10.1:12346"}
   subscribe_url = ceilometer_url + 'v2/subscribe'
   response = requests.post(subscribe_url, data=json.dumps(subscribe_data))
   print 'SRIKANTH: Ceilometer Subscription status:%s' % response.text
   #TODO: Fix the typo in 'sucess'
   if (not 'sucess' in response.text) and (not 'already exists' in response.text):
       print 'SRIKANTH: Ceilometer Subscription unsuccessful...Exiting'
       return
   periodic_cpu_threshold_evaluator()
   periodic_print()

if __name__ == "__main__":
   main()
