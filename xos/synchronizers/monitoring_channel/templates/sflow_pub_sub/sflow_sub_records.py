#!/usr/bin/python
import fnmatch
import logging

class sflow_sub_record:
    def __init__(self,scheme,app_id,app_ip,app_port,subscription_info,sub_info_filter):
        logging.debug("* Updating subscription_info ") 
        self.scheme = scheme
        self.app_id = app_id
        self.ipaddress = app_ip 
        self.portno = app_port 
        self.subscription_info = subscription_info
        self.sub_info_filter = sub_info_filter 

sflow_sub_database=[] 
def add_sflow_sub_record(record):
    logging.info("* inside %s",add_sflow_sub_record.__name__)
    if not sflow_sub_database:
        logging.debug("* -----------List is EMpty -------------") 
        sflow_sub_database.append(record)
        logging.debug("* Subscription is sucessful") 
        return "Subscription is sucessful \n" 
    for x in sflow_sub_database:
        if (record.ipaddress == x.ipaddress) and (record.portno == x.portno) :
            logging.warning("* entry already exists\n")
            return "entry already exists \n" 
    sflow_sub_database.append(record)
    return "Subscription is sucessful \n"
 
def delete_sflow_sub_record(ip,port):
    logging.info("* inside %s",delete_sflow_sub_record.__name__)
    Flag = False 
    for x in sflow_sub_database:
        if (ip == x.ipaddress) and (port == x.portno) :
            sflow_sub_database.remove(x)
            Flag = True
            logging.debug("* Un-Subscription is sucessful") 
            return "Un-Subscription is sucessful \n"
    if not Flag :
       err_str = "No subscription exists with target: udp://" + ip + ":" + str(port) + "\n"
       logging.error(err_str)
       raise Exception (err_str)
       
def print_sflow_sub_records():
    logging.info("* inside %s",print_sflow_sub_records.__name__)
    for obj in sflow_sub_database:
        logging.debug("* ------------------------------------------------") 
        logging.debug("* scheme:%s",obj.scheme)  
        logging.debug("* app_id:%s",obj.app_id)
        logging.debug("* portno:%s",obj.portno ) 
        logging.debug("* ipaddress:%s",obj.ipaddress)  
        logging.debug("* portno:%s",obj.portno)  
        logging.debug("* subscription_info:%s",obj.subscription_info)
        logging.debug("* sub_info_filter:%s",obj.sub_info_filter)
        logging.debug("* ------------------------------------------------")
 
def get_sflow_sub_records(notif_subscription_info):
    logging.info("* inside %s",get_sflow_sub_records.__name__)
    sub_list=[]  
    for obj in sflow_sub_database:
        if obj.subscription_info == notif_subscription_info:
            sub_list.append(obj)
    return sub_list
