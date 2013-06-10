try:
    from keystoneclient.v2_0 import client as keystone_client
    from glance import client as glance_client
    from novaclient.v1_1 import client as nova_client
    from quantumclient.v2_0 import client as quantum_client
    from nova.db.sqlalchemy import api as nova_db_api 
    from nova.context import get_admin_context
    has_openstack = True
except:
    has_openstack = False

from planetstack.config import Config

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
    def __init__(self, username=None, password=None, tenant=None, url=None, config=None, *args, **kwds):
        if config:
            config = Config(config)
        else:
            config = Config()
        self.has_openstack = has_openstack
        self.username = config.nova_admin_user
        self.password = config.nova_admin_password
        self.tenant = config.nova_admin_tenant
        self.url = config.nova_url

        if username:
            self.username = username
        if password:
            self.password = password
        if tenant:
            self.tenant = tenant
        if url:
            self.url = url

        if '@' in self.username:
            self.username = self.username[:self.username.index('@')]

class KeystoneClient(Client):
    def __init__(self, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.client = keystone_client.Client(username=self.username,
                                                 password=self.password,
                                                 tenant_name=self.tenant,
                                                 auth_url=self.url)

    @require_enabled
    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)

    @require_enabled
    def __getattr__(self, name):
        return getattr(self.client, name)


class GlanceClient(Client):
    def __init__(self, *args, **kwds):
        Client.__init__(self, *args, **kwds)
        if has_openstack:
            self.client = glance_client.get_client(host='0.0.0.0',
                                                   username=self.username,
                                                   password=self.password,
                                                   tenant=self.tenant,
                                                   auth_url=self.url)
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
            api.FLAGS(default_config_files=['/etc/nova/nova.conf'])
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
                                                auth_url=self.url)
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
        self.glance = GlanceClient(*args, **kwds)
        self.nova = NovaClient(*args, **kwds)
        self.nova_db = NovaDB(*args, **kwds)
        self.quantum = QuantumClient(*args, **kwds)

    @require_enabled
    def connect(self, *args, **kwds):
        self.__init__(*args, **kwds)

    @require_enabled
    def authenticate(self):
        return self.keystone.authenticate()
