import six
import uuid
import datetime
from kombu.connection import BrokerConnection
from kombu.messaging import Exchange, Queue, Consumer, Producer
import subprocess
import re
import time, threading
import sys, getopt
import logging
import os


logfile = "vcpe_stats_notifier.log"
level=logging.INFO
logger=logging.getLogger('vcpe_stats_notifier')
logger.setLevel(level)
# create formatter
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
handler=logging.handlers.RotatingFileHandler(logfile,maxBytes=1000000, backupCount=1)
# add formatter to handler
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_all_docker_containers():
    p = subprocess.Popen('docker ps --no-trunc', shell=True, stdout=subprocess.PIPE) 
    firstline = True
    dockercontainers = {}
    while True:
        out = p.stdout.readline()
        if out == '' and p.poll() != None:
            break
        if out != '':
            if firstline is True:
                firstline = False
            else:
                fields = out.split()
                container_fields = {}
                container_fields['id'] = fields[0]
                dockercontainers[fields[-1]] = container_fields
    return dockercontainers

def extract_compute_stats_from_all_vcpes(dockercontainers):
    for k,v in dockercontainers.iteritems():
        cmd = 'sudo docker stats --no-stream=true ' + v['id'] 
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) 
        firstline = True
        while True:
            out = p.stdout.readline()
            if out == '' and p.poll() != None:
                break
            if out != '':
                if firstline is True:
                    firstline = False
                else:
                    fields = out.split()
                    #['CONTAINER_ID', 'CPU%', 'MEMUSE', 'UNITS', '/', 'MEMLIMIT', 'UNITS', 'MEM%', 'NET I/O', 'UNITS', '/', 'NET I/O LIMIT', 'UNITS', 'BLOCK I/O', 'UNITS', '/', 'BLOCK I/O LIMIT', 'UNITS']
                    v['cpu_util'] = fields[1][:-1]
                    if fields[6] == 'GB':
                       v['memory'] = str(float(fields[5]) * 1000)
                    else:
                       v['memory'] = fields[5]
                    if fields[3] == 'GB':
                       v['memory_usage'] = str(float(fields[2]) * 1000)
                    else:
                       v['memory_usage'] = fields[2]
        v['network_stats'] = []
        for intf in ['eth0', 'eth1']:
            cmd = 'sudo docker exec ' + v['id'] + ' ifconfig ' + intf
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            out,err = p.communicate()
            if out:
                intf_stats = {}
                m = re.search("RX bytes:(\d+)", str(out))
                if m:
                    intf_stats['rx_bytes'] = m.group(1)
                m = re.search("TX bytes:(\d+)", str(out))
                if m:
                    intf_stats['tx_bytes'] = m.group(1)
                m = re.search("RX packets:(\d+)", str(out))
                if m:
                    intf_stats['rx_packets'] = m.group(1)
                m = re.search("TX packets:(\d+)", str(out))
                if m:
                    intf_stats['tx_packets'] = m.group(1)
                if intf_stats:
                    intf_stats['intf'] = intf
                    v['network_stats'].append(intf_stats)

def extract_dns_stats_from_all_vcpes(dockercontainers):
    for k,v in dockercontainers.iteritems():
         cmd = 'docker exec ' + v['id'] + ' killall -10 dnsmasq'
         p = subprocess.Popen (cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
         (output, error) = p.communicate()
         if error:
             logger.error("killall dnsmasq command failed with error = %s",error)
             continue
         cmd = 'docker exec ' + v['id'] + ' tail -7 /var/log/syslog'
         p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
         (output, error) = p.communicate()
         if error:
             logger.error("tail on dnsmasq log command failed with error = %s",error)
             continue
         log_list = output.splitlines()
         i = 0
         while i < len(log_list):
             m = re.search('(?<=:\scache size\s)(\S*)(?=,\s),\s(\S*)(?=/)/(\S*)(?=\scache insertions re-used unexpired cache entries)', log_list[i])
             if m == None:
                 i = i+1
                 continue;
             v['cache_size'] = m.group(1)
             v['replaced_unexpired_entries'] = m.group(2)
             v['total_inserted_entries'] = m.group(3)
             i = i+1
             m = re.search('(?<=:\squeries forwarded\s)(\S*)(?=,),\squeries answered locally\s(\S*)(?=$)', log_list[i])
             v['queries_forwarded'] = m.group(1)
             v['queries_answered_locally'] = m.group(2)
             break;
         i = i+2
         v['server_stats'] = []
         while i < len(log_list):
             m = re.search('(?<=:\sserver\s)(\S*)(?=#)#\d*:\squeries sent\s(\S*)(?=,),\sretried or failed\s(\S*)(?=$)', log_list[i])
             if m == None:
                 i = i+1
                 continue
             dns_server = {}
             dns_server['id'] = m.group(1)
             dns_server['queries_sent'] = m.group(2)
             dns_server['queries_failed'] = m.group(3)
             v['server_stats'].append(dns_server)
             i = i+1
    return dockercontainers


keystone_tenant_id='3a397e70f64e4e40b69b6266c634d9d0'
keystone_user_id='1e3ce043029547f1a61c1996d1a531a2'
rabbit_user='openstack'
rabbit_password='80608318c273f348a7c3'
rabbit_host='10.11.10.1'
vcpeservice_rabbit_exchange='vcpeservice'
cpe_publisher_id='vcpe_publisher'

producer = None

def setup_rabbit_mq_channel():
     global producer
     global rabbit_user, rabbit_password, rabbit_host, vcpeservice_rabbit_exchange,cpe_publisher_id
     vcpeservice_exchange = Exchange(vcpeservice_rabbit_exchange, "topic", durable=False)
     # connections/channels
     connection = BrokerConnection(rabbit_host, rabbit_user, rabbit_password)
     logger.info('Connection to RabbitMQ server successful')
     channel = connection.channel()
     # produce
     producer = Producer(channel, exchange=vcpeservice_exchange, routing_key='notifications.info')
     p = subprocess.Popen('hostname', shell=True, stdout=subprocess.PIPE)
     (hostname, error) = p.communicate()
     cpe_publisher_id = cpe_publisher_id + '_on_' + hostname
     logger.info('cpe_publisher_id=%s',cpe_publisher_id)

def publish_cpe_stats():
     global producer
     global keystone_tenant_id, keystone_user_id, cpe_publisher_id

     logger.debug('publish_cpe_stats invoked')

     dockercontainers = get_all_docker_containers()
     cpe_container_compute_stats = extract_compute_stats_from_all_vcpes(dockercontainers)
     cpe_container_dns_stats = extract_dns_stats_from_all_vcpes(dockercontainers)

     for k,v in cpe_container_dns_stats.iteritems():
          msg = {'event_type': 'vcpe', 
                 'message_id':six.text_type(uuid.uuid4()),
                 'publisher_id': cpe_publisher_id,
                 'timestamp':datetime.datetime.now().isoformat(),
                 'priority':'INFO',
                 'payload': {'vcpe_id':k, 
                             'user_id':keystone_user_id, 
                             'tenant_id':keystone_tenant_id 
                            }
                }
          producer.publish(msg)
          logger.debug('Publishing vcpe event: %s', msg)

          compute_payload = {}
          if 'cpu_util' in v:
               compute_payload['cpu_util']= v['cpu_util']
          if 'memory' in v:
               compute_payload['memory']= v['memory']
          if 'memory_usage' in v:
               compute_payload['memory_usage']= v['memory_usage']
          if ('network_stats' in v) and (v['network_stats']):
               compute_payload['network_stats']= v['network_stats']
          if compute_payload:
               compute_payload['vcpe_id'] = k
               compute_payload['user_id'] = keystone_user_id
               compute_payload['tenant_id'] = keystone_tenant_id
               msg = {'event_type': 'vcpe.compute.stats', 
                      'message_id':six.text_type(uuid.uuid4()),
                      'publisher_id': cpe_publisher_id,
                      'timestamp':datetime.datetime.now().isoformat(),
                      'priority':'INFO',
                      'payload': compute_payload 
                     }
               producer.publish(msg)
               logger.debug('Publishing vcpe.dns.cache.size event: %s', msg)

          if 'cache_size' in v:
               msg = {'event_type': 'vcpe.dns.cache.size', 
                      'message_id':six.text_type(uuid.uuid4()),
                      'publisher_id': cpe_publisher_id,
                      'timestamp':datetime.datetime.now().isoformat(),
                      'priority':'INFO',
                      'payload': {'vcpe_id':k, 
                                  'user_id':keystone_user_id,
                                  'tenant_id':keystone_tenant_id, 
                                  'cache_size':v['cache_size'] 
                                 }
                     }
               producer.publish(msg)
               logger.debug('Publishing vcpe.dns.cache.size event: %s', msg)

          if 'total_inserted_entries' in v:
               msg = {'event_type': 'vcpe.dns.total_inserted_entries', 
                      'message_id':six.text_type(uuid.uuid4()),
                      'publisher_id': cpe_publisher_id,
                      'timestamp':datetime.datetime.now().isoformat(),
                      'priority':'INFO',
                      'payload': {'vcpe_id':k, 
                                  'user_id':keystone_user_id,
                                  'tenant_id':keystone_tenant_id, 
                                  'total_inserted_entries':v['total_inserted_entries'] 
                                 }
                     }
               producer.publish(msg)
               logger.debug('Publishing vcpe.dns.total_inserted_entries event: %s', msg)

          if 'replaced_unexpired_entries' in v:
               msg = {'event_type': 'vcpe.dns.replaced_unexpired_entries', 
                      'message_id':six.text_type(uuid.uuid4()),
                      'publisher_id': cpe_publisher_id,
                      'timestamp':datetime.datetime.now().isoformat(),
                      'priority':'INFO',
                      'payload': {'vcpe_id':k, 
                                  'user_id':keystone_user_id,
                                  'tenant_id':keystone_tenant_id, 
                                  'replaced_unexpired_entries':v['replaced_unexpired_entries'] 
                                 }
                     }
               producer.publish(msg)
               logger.debug('Publishing vcpe.dns.replaced_unexpired_entries event: %s', msg)

          if 'queries_forwarded' in v:
               msg = {'event_type': 'vcpe.dns.queries_forwarded', 
                      'message_id':six.text_type(uuid.uuid4()),
                      'publisher_id': cpe_publisher_id,
                      'timestamp':datetime.datetime.now().isoformat(),
                      'priority':'INFO',
                      'payload': {'vcpe_id':k, 
                                  'user_id':keystone_user_id,
                                  'tenant_id':keystone_tenant_id, 
                                  'queries_forwarded':v['queries_forwarded'] 
                                 }
                     }
               producer.publish(msg)
               logger.debug('Publishing vcpe.dns.queries_forwarded event: %s', msg)

          if 'queries_answered_locally' in v:
               msg = {'event_type': 'vcpe.dns.queries_answered_locally', 
                      'message_id':six.text_type(uuid.uuid4()),
                      'publisher_id': cpe_publisher_id,
                      'timestamp':datetime.datetime.now().isoformat(),
                      'priority':'INFO',
                      'payload': {'vcpe_id':k, 
                                  'user_id':keystone_user_id,
                                  'tenant_id':keystone_tenant_id, 
                                  'queries_answered_locally':v['queries_answered_locally'] 
                                 }
                     }
               producer.publish(msg)
               logger.debug('Publishing vcpe.dns.queries_answered_locally event: %s', msg)

          if 'server_stats' in v:
               for server in v['server_stats']:
                   msg = {'event_type': 'vcpe.dns.server.queries_sent', 
                          'message_id':six.text_type(uuid.uuid4()),
                          'publisher_id': cpe_publisher_id,
                          'timestamp':datetime.datetime.now().isoformat(),
                          'priority':'INFO',
                          'payload': {'vcpe_id':k, 
                                      'user_id':keystone_user_id,
                                      'tenant_id':keystone_tenant_id, 
                                      'upstream_server':server['id'],
                                      'queries_sent':server['queries_sent'] 
                                     }
                         }
                   producer.publish(msg)
                   logger.debug('Publishing vcpe.dns.server.queries_sent event: %s', msg)

                   msg = {'event_type': 'vcpe.dns.server.queries_failed', 
                          'message_id':six.text_type(uuid.uuid4()),
                          'publisher_id': cpe_publisher_id,
                          'timestamp':datetime.datetime.now().isoformat(),
                          'priority':'INFO',
                          'payload': {'vcpe_id':k, 
                                      'user_id':keystone_user_id,
                                      'tenant_id':keystone_tenant_id, 
                                      'upstream_server':server['id'],
                                      'queries_failed':server['queries_failed'] 
                                     }
                         }
                   producer.publish(msg)
                   logger.debug('Publishing vcpe.dns.server.queries_failed event: %s', msg)

def periodic_publish():
     publish_cpe_stats()
     #Publish every 5minutes
     threading.Timer(300, periodic_publish).start()

def main(argv):
   global keystone_tenant_id, keystone_user_id, rabbit_user, rabbit_password, rabbit_host, vcpeservice_rabbit_exchange
   try:
      opts, args = getopt.getopt(argv,"",["keystone_tenant_id=","keystone_user_id=","rabbit_host=","rabbit_user=","rabbit_password=","vcpeservice_rabbit_exchange="])
   except getopt.GetoptError:
      print 'vcpe_stats_notifier.py keystone_tenant_id=<keystone_tenant_id> keystone_user_id=<keystone_user_id> rabbit_host=<IP addr> rabbit_user=<user> rabbit_password=<password> vcpeservice_rabbit_exchange=<exchange name>'
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("--keystone_tenant_id"):
         keystone_tenant_id = arg
      elif opt in ("--keystone_user_id"):
         keystone_user_id = arg
      elif opt in ("--rabbit_user"):
         rabbit_user = arg
      elif opt in ("--rabbit_password"):
         rabbit_password = arg
      elif opt in ("--rabbit_host"):
         rabbit_host = arg
      elif opt in ("--vcpeservice_rabbit_exchange"):
         vcpeservice_rabbit_exchange = arg
   logger.info("vcpe_stats_notifier args:keystone_tenant_id=%s keystone_user_id=%s rabbit_user=%s rabbit_host=%s vcpeservice_rabbit_exchange=%s",keystone_tenant_id,keystone_user_id,rabbit_user,rabbit_host,vcpeservice_rabbit_exchange)
   setup_rabbit_mq_channel()
   periodic_publish()

if __name__ == "__main__":
   main(sys.argv[1:])
