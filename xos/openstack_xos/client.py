import urlparse
try:
    from keystoneclient.v2_0 import client as keystone_client
    #from glance import client as glance_client
    import glanceclient
    from novaclient.v1_1 import client as nova_client
    from neutronclient.v2_0 import client as quantum_client
    has_openstack = True
except:
    has_openstack = False

from xos.config import Config

def require_enabled(callable):
    def wrapper(*args, **kwds):
        if has_openstack:
            return callable(*args, **kwds)
        else:
            return None
    return wrapper

def parse_novarc(filename):
    opts = {}
    f = open(filename, 'r')
    for line in f:
        try:
            line = line.replace('export', '').strip()
            parts = line.split('=')
            if len(parts) > 1:
                value = parts[1].replace("\'", "")
                value = value.replace('\"', '')
                opts[parts[0]] = value
        except:
            pass
    f.close()
    return opts

class Client:
    def __init__(self, username=None, password=None, tenant=None, url=None, token=None, endpoint=None, controller=None, cacert=None, admin=True, *args, **kwds):
       
        self.has_openstack = has_openstack
        self.url = controller.auth_url
        if admin:
            self.username = controller.admin_user
            self.password = controller.admin_password
            self.tenant = controller.admin_tenant
        else:
            self.username = None
            self.password = None
            self.tenant = None

        if username:
            self.username = username
        if password:
            self.password = password
        if tenant:
            self.tenant = tenant
        if url:
            self.url = url
        if token:
            self.token = token    
        if endpoint:
            self.endpoint = endpoint

        self.cacert = cacert

        #if '@' in self.username:
        #    self.username = self.username[:self.username.index('@')]

class KeystoneClient(Client):
    def __init__(self, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.client = keystone_client.Client(username=self.username,
                                                 password=self.password,
                                                 tenant_name=self.tenant,
                                                 auth_url=self.url
                                                )

    @require_enabled
    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)

    @require_enabled
    def __getattr__(self, name):
        return getattr(self.client, name)


class Glance(Client):
    def __init__(self, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.client = glanceclient.get_client(host='0.0.0.0',
                                                   username=self.username,
                                                   password=self.password,
                                                   tenant=self.tenant,
                                                   auth_url=self.url)
    @require_enabled
    def __getattr__(self, name):
        return getattr(self.client, name)

class GlanceClient(Client):
    def __init__(self, version, endpoint, token, cacert=None, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.client = glanceclient.Client(version, 
                endpoint=endpoint, 
                token=token,
                cacert=cacert
            )

    @require_enabled
    def __getattr__(self, name):
        return getattr(self.client, name)        

class NovaClient(Client):
    def __init__(self, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.client = nova_client.Client(username=self.username,
                                             api_key=self.password,
                                             project_id=self.tenant,
                                             auth_url=self.url,
                                             region_name='',
                                             extensions=[],
                                             service_type='compute',
                                             service_name='',
                                             )

    @require_enabled
    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)

    @require_enabled
    def __getattr__(self, name):
        return getattr(self.client, name)

class NovaDB(Client):
    def __init__(self, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.ctx = get_admin_context()
            nova_db_api.FLAGS(default_config_files=['/etc/nova/nova.conf'])
            self.client = nova_db_api


    @require_enabled
    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)

    @require_enabled
    def __getattr__(self, name):
        return getattr(self.client, name)

class QuantumClient(Client):
    def __init__(self, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.client = quantum_client.Client(username=self.username,
                                                password=self.password,
                                                tenant_name=self.tenant,
                                                auth_url=self.url,
                                                ca_cert=self.cacert)
    @require_enabled
    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)

    @require_enabled
    def __getattr__(self, name):
        return getattr(self.client, name)

class OpenStackClient:
    """
    A simple native shell to the openstack backend services.
    This class can receive all nova calls to the underlying testbed
    """

    def __init__ ( self, *args, **kwds) :
        # instantiate managers
        self.keystone = KeystoneClient(*args, **kwds)
        url_parsed = urlparse.urlparse(self.keystone.url)
        hostname = url_parsed.netloc.split(':')[0]
        token = self.keystone.client.tokens.authenticate(username=self.keystone.username, password=self.keystone.password, tenant_name=self.keystone.tenant)
        glance_endpoint = self.keystone.service_catalog.url_for(service_type='image', endpoint_type='publicURL')
        
        self.glanceclient = GlanceClient('1', endpoint=glance_endpoint, token=token.id, **kwds)
        self.nova = NovaClient(*args, **kwds)
        # self.nova_db = NovaDB(*args, **kwds)
        self.quantum = QuantumClient(*args, **kwds)
    

    @require_enabled
    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)

    @require_enabled
    def authenticate(self):
        return self.keystone.authenticate()
