#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ceilometerclient import client
from os import environ as env
import keystoneclient.v2_0.client as ksclient
import re
import datetime
import time
from monitor.monitordriver import *
import pdb

def object_to_filter(model_name, pk):
    from core.models import *
    filter_dict = {
            'ControllerSlice':[ControllerSlice, 'tenant_id', 'project_id'],
            'Instance':[Instance, 'instance_id', 'resource_id'],
            'ControllerSite':[ControllerSite, 'tenant_id', 'project_id']
    }

    mod,field,tag = filter_dict[model_name]
    obj = mod.objects.get(pk=pk)
    return '%s=%s'%(tag,getattr(obj,field))


def cli_to_array(cli_query):
    '''This converts from the cli list of queries to what is required
    by the python api.
    so from:
    "this<=34;that=foo"
    to
    "[{field=this,op=le,value=34},{field=that,op=eq,value=foo}]"
    '''
    if cli_query is None:
        return None

    op_lookup = {'!=': 'ne',
                 '>=': 'ge',
                 '<=': 'le',
                 '>': 'gt',
                 '<': 'lt',
                 '=': 'eq'}

    def split_by_op(string):
        # two character split (<=,!=)
        frags = re.findall(r'([[a-zA-Z0-9_.]+)([><!]=)([^ -,\t\n\r\f\v]+)',
                           string)
        if len(frags) == 0:
            #single char split (<,=)
            frags = re.findall(r'([a-zA-Z0-9_.]+)([><=])([^ -,\t\n\r\f\v]+)',
                               string)
        return frags

    opts = []
    queries = cli_query.split(';')
    for q in queries:
        frag = split_by_op(q)
        if len(frag) > 1:
            raise ValueError('incorrect seperator %s in query "%s"' %
                             ('(should be ";")', q))
        if len(frag) == 0:
            raise ValueError('invalid query %s' % q)
        query = frag[0]
        opt = {}
        opt['field'] = query[0]
        opt['op'] = op_lookup[query[1]]
        opt['value'] = query[2]
        opts.append(opt)
    return opts

def meters_to_stats(meters):
    stats = DashboardStatistics()
    for m in meters:
        timestamp = m.duration_start
        stats['stat_list'].append({'timestamp':timestamp, 'value':m.sum})
        stats['sum']+=m.sum
        stats['average']+=m.sum
        stats['unit'] = 'ns'

    if (len(meters)):
        stats['average']/=len(meters)
    else:
        stats['average']=0
    return stats


class CeilometerDriver(MonitorDriver):
    def get_meter(self, meter, obj, pk, keystone=None):
        if (not keystone):
                keystone={}
                keystone['os_username']=env['OS_USERNAME']
                keystone['os_password']=env['OS_PASSWORD']
                keystone['os_auth_url']=env['OS_AUTH_URL']
                keystone['os_tenant_name']=env['OS_TENANT_NAME']
                keystone['os_cacert']=env['OS_CACERT']
                keystone['os_region_name']=env['OS_REGION_NAME']

                keystone['username']=env['OS_USERNAME']
                keystone['password']=env['OS_PASSWORD']
                keystone['auth_url']=env['OS_AUTH_URL']
                keystone['tenant_name']=env['OS_TENANT_NAME']
                keystone['cacert']=env['OS_CACERT']
                keystone['region_name']=env['OS_REGION_NAME']

        keystone['auth_plugin']=client.AuthPlugin(**keystone)

        ceilometer = client.get_client(2,**keystone)
        
        cur_ts = datetime.datetime.fromtimestamp(time.time()-86400)
        str_ts = cur_ts.strftime('%Y-%m-%dT%H:%M:%S')

        object_filter = object_to_filter(obj, pk)
        filter=';'.join([object_filter,'timestamp>%s'%str_ts])
        #query = cli_to_array("project_id=124de34266b24f57957345cdb43cc9ff;timestamp>2014-12-11T00:00:00")
        query = cli_to_array(filter)

        meters = ceilometer.statistics.list(meter,q=query,period=3600)

        stats = meters_to_stats(meters)
        return stats
