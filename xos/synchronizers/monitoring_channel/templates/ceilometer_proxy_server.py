#!/usr/bin/env python
import web
import ConfigParser
import io
import json
from ceilometerclient import client
import logging
import urllib
import urllib2
from urlparse import urlparse
from wsgilog import WsgiLog

web.config.debug=False

logfile = "ceilometer_proxy_server.log"
level=logging.INFO
logger=logging.getLogger('ceilometer_proxy_server')
logger.setLevel(level)
handler=logging.handlers.RotatingFileHandler(logfile,maxBytes=1000000, backupCount=1)
logger.addHandler(handler)

class FileLog(WsgiLog):
    def __init__(self, application):
        WsgiLog.__init__(
            self,
            application,
            logformat = '%(message)s',
            tofile = True,
            toprint = True,
            prnlevel = level,
            file = logfile,
            backups =1
            )
    def __call__(self, environ, start_response):
        def hstart_response(status, response_headers, *args):
             out = start_response(status, response_headers, *args)
             try:
                 logline=environ["SERVER_PROTOCOL"]+" "+environ["REQUEST_METHOD"]+" "+environ["REQUEST_URI"]+" - "+status
             except err:
                 logline="Could not log <%s> due to err <%s>" % (str(environ), err)
             logger.info(logline)

             return out

        return super(FileLog, self).__call__(environ, hstart_response)

#TODOs:
#-See if we can avoid using python-ceilometerclient and instead use the REST calls directly with AuthToken
#
urls = (
    r'^/v2/meters$', 'meter_list',
    r'^/v2/meters/(?P<meter_name>[A-Za-z0-9_:.\-]+)/statistics$', 'statistics_list',
    r'^/v2/samples$', 'sample_list',
    r'^/v2/resources$', 'resource_list',
    r'^/v2/subscribe$', 'pubsub_handler',
)

app = web.application(urls, globals())

config = None
ceilometer_client = None


def parse_ceilometer_proxy_config():
    global config
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('ceilometer_proxy_config')
 
def ceilometerclient():
    global config, ceilometer_client
    if ceilometer_client:
         return ceilometer_client

    if not config:
         parse_ceilometer_proxy_config()

    keystone = {}
    keystone['os_username']=config.get('default','admin_user')
    keystone['os_password']=config.get('default','admin_password')
    keystone['os_auth_url']=config.get('default','auth_url')
    keystone['os_tenant_name']=config.get('default','admin_tenant')
    ceilometer_client = client.get_client(2,**keystone)
    logger.info('ceilometer get_client is successful')
    return ceilometer_client

def make_query(user_id=None, tenant_id=None, resource_id=None,
               user_ids=None, tenant_ids=None, resource_ids=None):
    """Returns query built from given parameters.

    This query can be then used for querying resources, meters and
    statistics.

    :Parameters:
      - `user_id`: user_id, has a priority over list of ids
      - `tenant_id`: tenant_id, has a priority over list of ids
      - `resource_id`: resource_id, has a priority over list of ids
      - `user_ids`: list of user_ids
      - `tenant_ids`: list of tenant_ids
      - `resource_ids`: list of resource_ids
    """
    user_ids = user_ids or []
    tenant_ids = tenant_ids or []
    resource_ids = resource_ids or []

    query = []
    if user_id:
        user_ids = [user_id]
    for u_id in user_ids:
        query.append({"field": "user_id", "op": "eq", "value": u_id})

    if tenant_id:
        tenant_ids = [tenant_id]
    for t_id in tenant_ids:
        query.append({"field": "project_id", "op": "eq", "value": t_id})

    if resource_id:
        resource_ids = [resource_id]
    for r_id in resource_ids:
        query.append({"field": "resource_id", "op": "eq", "value": r_id})

    return query

def filter_query_params(query_params):
    new_query=[]
    i=0
    user_specified_tenants=[]
    for field in query_params['q.field']:
        if (field != 'project_id') and (field != 'project'):
            query = {}
            query['field']=field
            if query_params['q.op'][i] != '':
                 query['op']=query_params['q.op'][i]
            query['value']=query_params['q.value'][i]
            new_query.append(query)
        else:
            user_specified_tenants.append(query_params['q.value'][i])
        i=i+1
    return new_query,user_specified_tenants

class meter_list:
    def GET(self):
        global config
        keyword_args = {
             "q.field": [],
             "q.op": [],
             "q.type": [],
             "q.value": [],
        }
        query_params = web.input(**keyword_args)
        new_query, user_specified_tenants = filter_query_params(query_params)

        client = ceilometerclient()
        meters=[]
        for (k,v) in config.items('allowed_tenants'):
             if user_specified_tenants and (k not in user_specified_tenants):
                 continue
             final_query=[]
             final_query.extend(new_query)
             query = make_query(tenant_id=k)
             final_query.extend(query)
             logger.debug('final query=%s',final_query)
             results = client.meters.list(q=final_query)
             meters.extend(results)
        return json.dumps([ob._info for ob in meters])

class statistics_list:
    def GET(self, meter_name):
        global config
        keyword_args = {
             "q.field": [],
             "q.op": [],
             "q.type": [],
             "q.value": [],
             "period": None
        }
        query_params = web.input(**keyword_args)
        new_query, user_specified_tenants = filter_query_params(query_params)

        client = ceilometerclient()
        period = query_params.period
        statistics = []
        for (k,v) in config.items('allowed_tenants'):
              if user_specified_tenants and (k not in user_specified_tenants):
                  continue
              final_query=[]
              final_query.extend(new_query)
              query = make_query(tenant_id=k)
              final_query.extend(query)
              logger.debug('final query=%s',final_query)
              results = client.statistics.list(meter_name=meter_name, q=final_query, period=period)
              statistics.extend(results)
        return json.dumps([ob._info for ob in statistics])

class sample_list:
    def GET(self):
        global config
        keyword_args = {
             "q.field": [],
             "q.op": [],
             "q.type": [],
             "q.value": [],
             "limit": None,
        }
        query_params = web.input(**keyword_args)
        new_query, user_specified_tenants = filter_query_params(query_params)

        client = ceilometerclient()
        limit=query_params.limit
        samples=[]
        for (k,v) in config.items('allowed_tenants'):
              if user_specified_tenants and (k not in user_specified_tenants):
                  continue
              final_query=[]
              final_query.extend(new_query)
              query = make_query(tenant_id=k)
              final_query.extend(query)
              logger.debug('final query=%s',final_query)
              results = client.new_samples.list(q=final_query,limit=limit)
              samples.extend(results)
        return json.dumps([ob._info for ob in samples])

class resource_list:
    def GET(self):
        global config
        keyword_args = {
             "q.field": [],
             "q.op": [],
             "q.type": [],
             "q.value": [],
             "limit": None,
             "links": None,
        }
        query_params = web.input(**keyword_args)
        new_query, user_specified_tenants = filter_query_params(query_params)

        client = ceilometerclient()
        limit=query_params.limit
        links=query_params.links
        resources=[]
        for (k,v) in config.items('allowed_tenants'):
              if user_specified_tenants and (k not in user_specified_tenants):
                  continue
              final_query=[]
              final_query.extend(new_query)
              query = make_query(tenant_id=k)
              final_query.extend(query)
              logger.debug('final query=%s',final_query)
              results = client.resources.list(q=final_query, limit=limit, links=links)
              resources.extend(results)
        return json.dumps([ob._info for ob in resources])

class pubsub_handler:
    def POST(self):
        global config
        parse_ceilometer_proxy_config()
        ceilometer_pub_sub_url = config.get('default', 'ceilometer_pub_sub_url')
        url = urlparse(ceilometer_pub_sub_url)
        if (not url.scheme) or (not url.netloc): 
             raise Exception("Ceilometer PUB/SUB URL not set")
        ceilometer_pub_sub_url = url.scheme + "://" + url.netloc + "/subscribe"
        data_str = unicode(web.data(),'iso-8859-1')
        post_data = json.loads(data_str)
        final_query=[]
        for (k,v) in config.items('allowed_tenants'):
             query = make_query(tenant_id=k)
             final_query.extend(query)
        if not final_query:
             raise Exception("Not allowed to subscribe to any meters")
        post_data["query"] = final_query
        #TODO: The PUB/SUB url needs to be read from config
        put_request = urllib2.Request(ceilometer_pub_sub_url, json.dumps(post_data))
        put_request.get_method = lambda: 'SUB'
        put_request.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(put_request)
        response_text = response.read()
        return json.dumps(response_text)

    def DELETE(self):
        ceilometer_pub_sub_url = config.get('default', 'ceilometer_pub_sub_url')
        url = urlparse(ceilometer_pub_sub_url)
        if (not url.scheme) or (not url.netloc): 
             raise Exception("Ceilometer PUB/SUB URL not set")
        ceilometer_pub_sub_url = url.scheme + "://" + url.netloc + "/unsubscribe"
        data_str = web.data()
        #TODO: The PUB/SUB url needs to be read from config
        put_request = urllib2.Request(ceilometer_pub_sub_url, data_str)
        put_request.get_method = lambda: 'UNSUB'
        put_request.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(put_request)
        response_text = response.read()
        return json.dumps(response_text)

if __name__ == "__main__":
    app.run(FileLog)
