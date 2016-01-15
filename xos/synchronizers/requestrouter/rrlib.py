import os
import base64
import string
import sys
import socket
from sets import Set
if __name__ == '__main__':
    sys.path.append("/opt/xos")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")

from xos.config import Config
from core.models import Service
from services.requestrouter.models import RequestRouterService, ServiceMap
from xos.logger import Logger, logging
import rrlib_config

logger = Logger(level=logging.INFO)

'''
Conventions:
1) All dnsredir backend will listen at port 9000+ servicemap.pk ( where pk is the primary key generated in django model)
'''

class RequestRouterLibrary:

    def __init__(self):
        pass
    
    def gen_slice_info(self, service=None):   
        """generates instance information from slice of request router
        """

        if (service is None ):
            service = RequestRouterService.objects.get()

        mapping = {}
        #static mapping for demo purpose 
        #mapping["node47.princeton.vicci.org"] = "128.112.171.112"
        mapping["node48.princeton.vicci.org"] = "128.112.171.114"
    
        '''for slice in service.service.all():
            name = slice.name
            for instance in slice.instances.all():
                mapping[instance.name] = str(instance.ip)
        '''
        return mapping

    def gen_servicemap_slice_info(self, servicemap):
        """generates instance information from slice of servicemap
        """

        wzone = Set(['arizona', 'stanford', 'on.lab', 'housten']) # zone=1 in cooden.conf
        ezone = Set(['princeton', 'atlanta', 'new york', 'georgia tech']) # zone=2 in coodeen.conf

        mapping_zone = {}
        mapping_ip = {}
        slice = servicemap.slice
        name = slice.name
        for instance in slice.instances.all():
            mapping_ip[instance.node.name] = socket.gethostbyname(instance.node.name)
            #print "instance name "+instance.name+str(instance.ip)+"\n"
            site = instance.node.site.name
            if(site.lower() in wzone):
                mapping_zone[instance.node.name] = str(1)
            else:
                mapping_zone[instance.node.name] = str(2)

        return mapping_ip, mapping_zone



    def gen_slice_file(self, service):
        """ generates host file for the slice information
            to be used by ansible to push configuration files
        """

        mapping = self.gen_slice_info(service)

        fn = "/etc/ansible/requestrouter/dnsredir/hosts"
        f = open(fn, "w")
        for (k,v) in mapping.items():
            f.write("%s\n" % k)

        fn = "/etc/ansible/requestrouter/dnsdemux/hosts"
        f = open(fn, "w")
        for (k,v) in mapping.items():
            f.write("%s\n" % k)


    def get_servicemap_uid(self, servicemap):
        seq = ("service_", str(servicemap.pk));
        return "".join(seq)

    def get_service_port(self, servicemap):
                return str(9000+servicemap.pk)

    def gen_dnsredir_serviceconf(self, servicemap):
        objname = self.get_servicemap_uid(servicemap)
    
        rr_mapping = self.gen_slice_info(None)
    
        #generate dnsredir.conf file parameters to be used in static file.
        mapping = {}
        mapping["port_listen"] = self.get_service_port(servicemap)
        mapping["configdir"] = rrlib_config.DNSREDIR_CONFIGDIR_PREFIX+objname+".d/"
        mapping["logdir"] = rrlib_config.DNSREDIR_LOGDIR_PREFIX+objname+".d"
        mapping["pidfile"] = rrlib_config.DNSREDIR_PIDFILE_PREFIX+objname+".pid"
        mapping["domain_name"] = servicemap.prefix      
        mapping["heartbeat_port"] = rrlib_config.HEARTBEAT_PORT

        #generate dnsredir.conf file 

        fn = "./temp_config/dnsredir/"+objname+".conf"
        f = open(fn, "w")
        for (k,v) in rr_mapping.items():
                        f.write(mapping["domain_name"]+". NS "+k+". "+v+" 3600 \n" % mapping)


        f.write("""
Default_TTL 30

Port %(port_listen)s

ConfigDir %(configdir)s

MapsDir maps.d

HTTPPort %(heartbeat_port)d

PidFile %(pidfile)s

HttpRequestPort 8081

""" % mapping)

        #generate configdirectory
        
        os.mkdir("./temp_config/dnsredir/"+objname+".d")
        
        #geenrate codeen_nodes.conf
        mapping_ip, mapping_zone = self.gen_servicemap_slice_info(servicemap)

        codeen_name = "./temp_config/dnsredir/"+objname+".d/codeen_nodes.conf"
        f = open(codeen_name, "w")
        for (k,v) in mapping_zone.items():
            f.write(k+" zone="+v+" \n")

        iptxt = "./temp_config/dnsredir/"+objname+".d/node-to-ip.txt"
        f = open(iptxt, "w")
        for (k,v) in mapping_ip.items():
            f.write(k+" "+v+" \n")

        #generate maps directory
        os.mkdir("./temp_config/dnsredir/"+objname+".d/maps.d")

        # redirection map
        map = "./temp_config/dnsredir/"+objname+".d/maps.d/map.conf"
        f = open(map, "w")
		#hardcoded probable public IP masks from arizona and princeton region respectively
        f.write("prefix "+servicemap.prefix+" \n")
        f.write("map 150.135.211.252/32 zone 1 || zone 2 \n")
        f.write("map 128.112.171.112/24 zone 2 || zone 1 \n")
        f.write("map 0.0.0.0/0 zone 1 || zone 2 \n")


    def gen_dnsdemux_serviceconf(self, servicemap):
        '''
        generates frontend service*.conf file for each of the service
        It assumes that there is a dnsdemux frontend running on the RR istallation and will
        just add a conf file for each service in /etc/dnsdemux/default
        '''
        objname = self.get_servicemap_uid(servicemap)
        #generate dnsdemux.conf file parameters to be used in static file.
       
        port_listen = self.get_service_port(servicemap)
        domain_name = servicemap.prefix  
        #generate service specific .conf file

        rr_mapping = self.gen_slice_info(None)

        fn = "./temp_config/dnsdemux/"+objname+".conf"
        f = open(fn, "w")

        for (k,v) in rr_mapping.items():
            f.write("Forward "+v+" "+port_listen+" 8081 "+domain_name+".\n")

    
    def teardown_temp_configfiles(self, objname):
        if os.path.exists("./temp_config/dnsdemux/"+objname+".conf"):
            os.remove("./temp_config/dnsdemux/"+objname+".conf")
        if os.path.exists("./temp_config/dnsredir/"+objname+".d/maps.d/map.conf"):
            os.remove("./temp_config/dnsredir/"+objname+".d/maps.d/map.conf")
        if os.path.exists("./temp_config/dnsredir/"+objname+".d/maps.d"):
            os.rmdir("./temp_config/dnsredir/"+objname+".d/maps.d")
        if os.path.exists("./temp_config/dnsredir/"+objname+".d/node-to-ip.txt"):
            os.remove("./temp_config/dnsredir/"+objname+".d/node-to-ip.txt")
        if os.path.exists("./temp_config/dnsredir/"+objname+".d/codeen_nodes.conf"):
            os.remove("./temp_config/dnsredir/"+objname+".d/codeen_nodes.conf")
        if os.path.exists("./temp_config/dnsredir/"+objname+".d"):
            os.rmdir("./temp_config/dnsredir/"+objname+".d")
        if os.path.exists("./temp_config/dnsredir/"+objname+".conf"):
            os.remove("./temp_config/dnsredir/"+objname+".conf")

