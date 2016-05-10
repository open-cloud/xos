import requests
from six.moves import urllib
import urllib2
import pytz
import datetime
import time
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework.views import APIView
from core.models import *
from services.ceilometer.models import *
from django.forms import widgets
from django.utils import datastructures
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from xos.logger import observer_logger as logger

# This REST API endpoint provides information that the ceilometer view needs to display

def getTenantCeilometerProxyURL(user):
    monitoring_channel = None
    for obj in MonitoringChannel.get_tenant_objects().all():
        if (obj.creator.username == user.username):
            monitoring_channel = obj
            break
    if not monitoring_channel:
        raise XOSMissingField("Monitoring channel is missing for this tenant...Create one and invoke this REST API")
    #TODO: Wait until URL is completely UP
    MAX_ATTEMPTS = 5
    attempts = 0
    while True:
        try:
            response = urllib2.urlopen(monitoring_channel.ceilometer_url)
            break
        except urllib2.HTTPError, e:
            logger.info('HTTP error %(reason)s' % {'reason':e.reason})
            break
        except urllib2.URLError, e:
            attempts += 1
            if attempts >= MAX_ATTEMPTS:
                raise XOSServiceUnavailable("Ceilometer channel is not ready yet...Try again later")
            logger.info('URL error %(reason)s' % {'reason':e.reason})
            time.sleep(1)
            pass
    logger.info("Ceilometer proxy URL for user %(user)s is %(url)s" % {'user':user.username,'url':monitoring_channel.ceilometer_url})
    return monitoring_channel.ceilometer_url

def getTenantControllerTenantMap(user, slice=None):
    tenantmap={}
    if not slice:
        slices = Slice.objects.filter(creator=user)
    else:
        slices = [slice]
    for s in slices:
        for cs in s.controllerslices.all():
            if cs.tenant_id:
                tenantmap[cs.tenant_id] = {"slice": cs.slice.name}
                if cs.slice.service:
                    tenantmap[cs.tenant_id]["service"] = cs.slice.service.name
                else:
                    logger.warn("SRIKANTH: Slice %(slice)s is not associated with any service" % {'slice':cs.slice.name})
                    tenantmap[cs.tenant_id]["service"] = "Other"
    if not slice:
        #TEMPORARY WORK AROUND: There are some resource in network like whitebox switches does not belong to a specific tenant.
        #They are all associated with "default_admin_tenant" tenant
        tenantmap["default_admin_tenant"] = {"slice": "default_admin_tenant", "service": "Other"}
    return tenantmap

def build_url(path, q, params=None):
    """Convert list of dicts and a list of params to query url format.

    This will convert the following:
        "[{field=this,op=le,value=34},
          {field=that,op=eq,value=foo,type=string}],
         ['foo=bar','sna=fu']"
    to:
        "?q.field=this&q.field=that&
          q.op=le&q.op=eq&
          q.type=&q.type=string&
          q.value=34&q.value=foo&
          foo=bar&sna=fu"
    """
    if q:
        query_params = {'q.field': [],
                        'q.value': [],
                        'q.op': [],
                        'q.type': []}

        for query in q:
            for name in ['field', 'op', 'value', 'type']:
                query_params['q.%s' % name].append(query.get(name, ''))

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        new_qparams = sorted(query_params.items(), key=lambda x: x[0])
        path += "?" + urllib.parse.urlencode(new_qparams, doseq=True)

        if params:
            for p in params:
                path += '&%s' % p
    elif params:
        path += '?%s' % params[0]
        for p in params[1:]:
            path += '&%s' % p
    return path

def concat_url(endpoint, url):
    """Concatenate endpoint and final URL.

    E.g., "http://keystone/v2.0/" and "/tokens" are concatenated to
    "http://keystone/v2.0/tokens".

    :param endpoint: the base URL
    :param url: the final URL
    """
    return "%s/%s" % (endpoint.rstrip("/"), url.strip("/"))

def resource_list(request, query=None, ceilometer_url=None, ceilometer_usage_object=None):
    """List the resources."""
    url = concat_url(ceilometer_url, build_url('/v2/resources', query))
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise e
    return response.json()

def sample_list(request, meter_name, ceilometer_url=None, query=None, limit=None):
    """List the samples for this meters."""
    params = ['limit=%s' % limit] if limit else []
    url = concat_url(ceilometer_url, build_url('/v2/samples', query, params))
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise e
    return response.json()

def meter_list(request, ceilometer_url=None, query=None):
    """List the user's meters."""
    url = concat_url(ceilometer_url, build_url('/v2/meters', query))
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise e
    return response.json()


def statistic_list(request, meter_name, ceilometer_url=None, query=None, period=None):
    """List of statistics."""
    p = ['period=%s' % period] if period else []
    url = concat_url(ceilometer_url, build_url('/v2/meters/' + meter_name + '/statistics', query, p))
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise e
    return response.json()

def diff_lists(a, b):
    if not a:
        return []
    elif not b:
        return a
    else:
        return list(set(a) - set(b))

def get_resource_map(request, ceilometer_url, query=None):
    resource_map = {}
    try:
        resources = resource_list(request, ceilometer_url=ceilometer_url, query=query)
        for r in resources:
            if 'display_name' in r['metadata']:
                name = r['metadata']['display_name']
            elif 'name' in r['metadata']:
                name = r['metadata']['name']
            else:
                name = r['resource_id']
            resource_map[r['resource_id']] = name
    except requests.exceptions.RequestException as e:
        raise e

    return resource_map

class Meters(object):
    """Class for listing of available meters.

    It is listing meters defined in this class that are available
    in Ceilometer meter_list.

    It is storing information that is not available in Ceilometer, i.e.
    label, description.

    """

    def __init__(self, request=None, ceilometer_meter_list=None, ceilometer_url=None, query=None, tenant_map=None, resource_map=None):
        # Storing the request.
        self._request = request
        self.ceilometer_url = ceilometer_url
        self.tenant_map = tenant_map
        self.resource_map = resource_map

        # Storing the Ceilometer meter list
        if ceilometer_meter_list:
            self._ceilometer_meter_list = ceilometer_meter_list
        else:
            try:
                meter_query=[]
                if query:
                    meter_query = query
                self._ceilometer_meter_list = meter_list(request, self.ceilometer_url, meter_query)
            except requests.exceptions.RequestException as e:
                self._ceilometer_meter_list = []
                raise e

        # Storing the meters info categorized by their services.
        self._nova_meters_info = self._get_nova_meters_info()
        self._neutron_meters_info = self._get_neutron_meters_info()
        self._glance_meters_info = self._get_glance_meters_info()
        self._cinder_meters_info = self._get_cinder_meters_info()
        self._swift_meters_info = self._get_swift_meters_info()
        self._kwapi_meters_info = self._get_kwapi_meters_info()
        self._ipmi_meters_info = self._get_ipmi_meters_info()
        self._vcpe_meters_info = self._get_vcpe_meters_info()
        self._volt_meters_info = self._get_volt_meters_info()
        self._sdn_meters_info = self._get_sdn_meters_info()

        # Storing the meters info of all services together.
        all_services_meters = (self._nova_meters_info,
                               self._neutron_meters_info,
                               self._glance_meters_info,
                               self._cinder_meters_info,
                               self._swift_meters_info,
                               self._kwapi_meters_info,
                               self._ipmi_meters_info,
                               self._vcpe_meters_info,
                               self._volt_meters_info,
                               self._sdn_meters_info)
        self._all_meters_info = {}
        for service_meters in all_services_meters:
            self._all_meters_info.update(dict([(meter_name, meter_info)
                                               for meter_name, meter_info
                                               in service_meters.items()]))

        # Here will be the cached Meter objects, that will be reused for
        # repeated listing.
        self._cached_meters = {}

    def list_all(self, only_meters=None, except_meters=None):
        """Returns a list of meters based on the meters names.

        :Parameters:
          - `only_meters`: The list of meter names we want to show.
          - `except_meters`: The list of meter names we don't want to show.
        """

        return self._list(only_meters=only_meters,
                          except_meters=except_meters)

    def list_nova(self, except_meters=None):
        """Returns a list of meters tied to nova.

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show.
        """

        return self._list(only_meters=self._nova_meters_info.keys(),
                          except_meters=except_meters)

    def list_neutron(self, except_meters=None):
        """Returns a list of meters tied to neutron.

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show.
        """

        return self._list(only_meters=self._neutron_meters_info.keys(),
                          except_meters=except_meters)

    def list_glance(self, except_meters=None):
        """Returns a list of meters tied to glance.

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show.
        """

        return self._list(only_meters=self._glance_meters_info.keys(),
                          except_meters=except_meters)

    def list_cinder(self, except_meters=None):
        """Returns a list of meters tied to cinder.

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show.
        """

        return self._list(only_meters=self._cinder_meters_info.keys(),
                          except_meters=except_meters)

    def list_swift(self, except_meters=None):
        """Returns a list of meters tied to swift.

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show.
        """

        return self._list(only_meters=self._swift_meters_info.keys(),
                          except_meters=except_meters)

    def list_kwapi(self, except_meters=None):
        """Returns a list of meters tied to kwapi.

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show.
        """

        return self._list(only_meters=self._kwapi_meters_info.keys(),
                          except_meters=except_meters)

    def list_ipmi(self, except_meters=None):
        """Returns a list of meters tied to ipmi

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show
        """

        return self._list(only_meters=self._ipmi_meters_info.keys(),
                          except_meters=except_meters)

    def list_vcpe(self, except_meters=None):
        """Returns a list of meters tied to vcpe service

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show
        """

        return self._list(only_meters=self._vcpe_meters_info.keys(),
                          except_meters=except_meters)

    def list_volt(self, except_meters=None):
        """Returns a list of meters tied to volt service

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show
        """

        return self._list(only_meters=self._volt_meters_info.keys(),
                          except_meters=except_meters)

    def list_sdn(self, except_meters=None):
        """Returns a list of meters tied to sdn service

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show
        """

        return self._list(only_meters=self._sdn_meters_info.keys(),
                          except_meters=except_meters)

    def list_other_services(self, except_meters=None):
        """Returns a list of meters tied to ipmi

        :Parameters:
          - `except_meters`: The list of meter names we don't want to show
        """
        other_service_meters = [m for m in self._ceilometer_meter_list
                                if m.name not in self._all_meters_info.keys()]
        other_service_meters = diff_lists(other_service_meters, except_meters)

        meters = []
        for meter in other_service_meters:
            self._cached_meters[meter.name] = meter
            meters.append(meter)
        return meters

    def _list(self, only_meters=None, except_meters=None):
        """Returns a list of meters based on the meters names.

        :Parameters:
          - `only_meters`: The list of meter names we want to show.
          - `except_meters`: The list of meter names we don't want to show.
        """

        # Get all wanted meter names.
        if only_meters:
            meter_names = only_meters
        else:
            meter_names = [meter_name for meter_name
                           in self._all_meters_info.keys()]

        meter_names = diff_lists(meter_names, except_meters)
        # Collect meters for wanted meter names.
        return self._get_meters(meter_names)

    def _get_meters(self, meter_names):
        """Obtain meters based on meter_names.

        The meters that do not exist in Ceilometer meter list are left out.

        :Parameters:
          - `meter_names`: A list of meter names we want to fetch.
        """

        meters = []
        for meter_name in meter_names:
            meter_candidates = self._get_meter(meter_name)
            if meter_candidates:
                meters.extend(meter_candidates)
        return meters

    def _get_meter(self, meter_name):
        """Obtains a meter.

        Obtains meter either from cache or from Ceilometer meter list
        joined with statically defined meter info like label and description.

        :Parameters:
          - `meter_name`: A meter name we want to fetch.
        """
        meter_candidates = self._cached_meters.get(meter_name, None)
        if not meter_candidates:
            meter_candidates = [m for m in self._ceilometer_meter_list
                                if m["name"] == meter_name]

            if meter_candidates:
                meter_info = self._all_meters_info.get(meter_name, None)
                if meter_info:
                    label = meter_info["label"]
                    description = meter_info["description"]
                    meter_category = meter_info["type"]
                else:
                    label = ""
                    description = ""
                    meter_category = "Other"
                for meter in meter_candidates:
                    meter["label"] = label
                    meter["description"] = description
                    meter["category"] = meter_category
                    if meter["project_id"] in self.tenant_map.keys():
                        meter["slice"] = self.tenant_map[meter["project_id"]]["slice"]
                        meter["service"] = self.tenant_map[meter["project_id"]]["service"]
                    else:
                        meter["slice"] = meter["project_id"]
                        meter["service"] = "Other"
                    if meter["resource_id"] in self.resource_map.keys():
                        meter["resource_name"] = self.resource_map[meter["resource_id"]]

                self._cached_meters[meter_name] = meter_candidates

        return meter_candidates

    def _get_nova_meters_info(self):
        """Returns additional info for each meter.

        That will be used for augmenting the Ceilometer meter.
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        meters_info = datastructures.SortedDict([
            ("instance", {
                'type': _("Nova"),
                'label': '',
                'description': _("Existence of instance"),
            }),
            ("instance:<type>", {
                'type': _("Nova"),
                'label': '',
                'description': _("Existence of instance <type> "
                                 "(openstack types)"),
            }),
            ("memory", {
                'type': _("Nova"),
                'label': '',
                'description': _("Volume of RAM"),
            }),
            ("memory.usage", {
                'type': _("Nova"),
                'label': '',
                'description': _("Volume of RAM used"),
            }),
            ("cpu", {
                'type': _("Nova"),
                'label': '',
                'description': _("CPU time used"),
            }),
            ("cpu_util", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average CPU utilization"),
            }),
            ("vcpus", {
                'type': _("Nova"),
                'label': '',
                'description': _("Number of VCPUs"),
            }),
            ("disk.read.requests", {
                'type': _("Nova"),
                'label': '',
                'description': _("Number of read requests"),
            }),
            ("disk.write.requests", {
                'type': _("Nova"),
                'label': '',
                'description': _("Number of write requests"),
            }),
            ("disk.read.bytes", {
                'type': _("Nova"),
                'label': '',
                'description': _("Volume of reads"),
            }),
            ("disk.write.bytes", {
                'type': _("Nova"),
                'label': '',
                'description': _("Volume of writes"),
            }),
            ("disk.read.requests.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average rate of read requests"),
            }),
            ("disk.write.requests.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average rate of write requests"),
            }),
            ("disk.read.bytes.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average rate of reads"),
            }),
            ("disk.write.bytes.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average volume of writes"),
            }),
            ("disk.root.size", {
                'type': _("Nova"),
                'label': '',
                'description': _("Size of root disk"),
            }),
            ("disk.ephemeral.size", {
                'type': _("Nova"),
                'label': '',
                'description': _("Size of ephemeral disk"),
            }),
            ("network.incoming.bytes", {
                'type': _("Nova"),
                'label': '',
                'description': _("Number of incoming bytes "
                                 "on the network for a VM interface"),
            }),
            ("network.outgoing.bytes", {
                'type': _("Nova"),
                'label': '',
                'description': _("Number of outgoing bytes "
                                 "on the network for a VM interface"),
            }),
            ("network.incoming.packets", {
                'type': _("Nova"),
                'label': '',
                'description': _("Number of incoming "
                                 "packets for a VM interface"),
            }),
            ("network.outgoing.packets", {
                'type': _("Nova"),
                'label': '',
                'description': _("Number of outgoing "
                                 "packets for a VM interface"),
            }),
            ("network.incoming.bytes.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average rate per sec of incoming "
                                 "bytes on a VM network interface"),
            }),
            ("network.outgoing.bytes.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average rate per sec of outgoing "
                                 "bytes on a VM network interface"),
            }),
            ("network.incoming.packets.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average rate per sec of incoming "
                                 "packets on a VM network interface"),
            }),
            ("network.outgoing.packets.rate", {
                'type': _("Nova"),
                'label': '',
                'description': _("Average rate per sec of outgoing "
                                 "packets on a VM network interface"),
            }),
        ])
        # Adding flavor based meters into meters_info dict
        # TODO(lsmola) this kind of meter will be probably deprecated
        # https://bugs.launchpad.net/ceilometer/+bug/1208365 . Delete it then.
        #for flavor in get_flavor_names(self._request):
        #    name = 'instance:%s' % flavor
        #    meters_info[name] = dict(meters_info["instance:<type>"])

        #    meters_info[name]['description'] = (
        #        _('Duration of instance type %s (openstack flavor)') %
        #        flavor)

        # TODO(lsmola) allow to set specific in local_settings. For all meters
        # because users can have their own agents and meters.
        return meters_info

    def _get_neutron_meters_info(self):
        """Returns additional info for each meter.

        That will be used for augmenting the Ceilometer meter.
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('network', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Existence of network"),
            }),
            ('network.create', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Creation requests for this network"),
            }),
            ('network.update', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Update requests for this network"),
            }),
            ('subnet', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Existence of subnet"),
            }),
            ('subnet.create', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Creation requests for this subnet"),
            }),
            ('subnet.update', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Update requests for this subnet"),
            }),
            ('port', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Existence of port"),
            }),
            ('port.create', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Creation requests for this port"),
            }),
            ('port.update', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Update requests for this port"),
            }),
            ('router', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Existence of router"),
            }),
            ('router.create', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Creation requests for this router"),
            }),
            ('router.update', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Update requests for this router"),
            }),
            ('ip.floating', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Existence of floating ip"),
            }),
            ('ip.floating.create', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Creation requests for this floating ip"),
            }),
            ('ip.floating.update', {
                'type': _("Neutron"),
                'label': '',
                'description': _("Update requests for this floating ip"),
            }),
        ])

    def _get_glance_meters_info(self):
        """Returns additional info for each meter.

        That will be used for augmenting the Ceilometer meter.
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('image', {
                'type': _("Glance"),
                'label': '',
                'description': _("Image existence check"),
            }),
            ('image.size', {
                'type': _("Glance"),
                'label': '',
                'description': _("Uploaded image size"),
            }),
            ('image.update', {
                'type': _("Glance"),
                'label': '',
                'description': _("Number of image updates"),
            }),
            ('image.upload', {
                'type': _("Glance"),
                'label': '',
                'description': _("Number of image uploads"),
            }),
            ('image.delete', {
                'type': _("Glance"),
                'label': '',
                'description': _("Number of image deletions"),
            }),
            ('image.download', {
                'type': _("Glance"),
                'label': '',
                'description': _("Image is downloaded"),
            }),
            ('image.serve', {
                'type': _("Glance"),
                'label': '',
                'description': _("Image is served out"),
            }),
        ])

    def _get_cinder_meters_info(self):
        """Returns additional info for each meter.

        That will be used for augmenting the Ceilometer meter.
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('volume', {
                'type': _("Cinder"),
                'label': '',
                'description': _("Existence of volume"),
            }),
            ('volume.size', {
                'type': _("Cinder"),
                'label': '',
                'description': _("Size of volume"),
            }),
        ])

    def _get_swift_meters_info(self):
        """Returns additional info for each meter.

        That will be used for augmenting the Ceilometer meter.
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('storage.objects', {
                'type': _("Swift"),
                'label': '',
                'description': _("Number of objects"),
            }),
            ('storage.objects.size', {
                'type': _("Swift"),
                'label': '',
                'description': _("Total size of stored objects"),
            }),
            ('storage.objects.containers', {
                'type': _("Swift"),
                'label': '',
                'description': _("Number of containers"),
            }),
            ('storage.objects.incoming.bytes', {
                'type': _("Swift"),
                'label': '',
                'description': _("Number of incoming bytes"),
            }),
            ('storage.objects.outgoing.bytes', {
                'type': _("Swift"),
                'label': '',
                'description': _("Number of outgoing bytes"),
            }),
            ('storage.api.request', {
                'type': _("Swift"),
                'label': '',
                'description': _("Number of API requests against swift"),
            }),
        ])

    def _get_kwapi_meters_info(self):
        """Returns additional info for each meter.

        That will be used for augmenting the Ceilometer meter.
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('energy', {
                'type': _("Kwapi"),
                'label': '',
                'description': _("Amount of energy"),
            }),
            ('power', {
                'type': _("Kwapi"),
                'label': '',
                'description': _("Power consumption"),
            }),
        ])

    def _get_ipmi_meters_info(self):
        """Returns additional info for each meter

        That will be used for augmenting the Ceilometer meter
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('hardware.ipmi.node.power', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System Current Power"),
            }),
            ('hardware.ipmi.fan', {
                'type': _("IPMI"),
                'label': '',
                'description': _("Fan RPM"),
            }),
            ('hardware.ipmi.temperature', {
                'type': _("IPMI"),
                'label': '',
                'description': _("Sensor Temperature Reading"),
            }),
            ('hardware.ipmi.current', {
                'type': _("IPMI"),
                'label': '',
                'description': _("Sensor Current Reading"),
            }),
            ('hardware.ipmi.voltage', {
                'type': _("IPMI"),
                'label': '',
                'description': _("Sensor Voltage Reading"),
            }),
            ('hardware.ipmi.node.inlet_temperature', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System Inlet Temperature Reading"),
            }),
            ('hardware.ipmi.node.outlet_temperature', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System Outlet Temperature Reading"),
            }),
            ('hardware.ipmi.node.airflow', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System Airflow Reading"),
            }),
            ('hardware.ipmi.node.cups', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System CUPS Reading"),
            }),
            ('hardware.ipmi.node.cpu_util', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System CPU Utility Reading"),
            }),
            ('hardware.ipmi.node.mem_util', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System Memory Utility Reading"),
            }),
            ('hardware.ipmi.node.io_util', {
                'type': _("IPMI"),
                'label': '',
                'description': _("System IO Utility Reading"),
            }),
        ])

    def _get_vcpe_meters_info(self):
        """Returns additional info for each meter

        That will be used for augmenting the Ceilometer meter
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('vsg', {
                'type': _("VSG"),
                'label': '',
                'description': _("Existence of vsg instance"),
            }),
            ('vsg.dns.cache.size', {
                'type': _("VSG"),
                'label': '',
                'description': _("Number of entries in DNS cache"),
            }),
            ('vsg.dns.total_instered_entries', {
                'type': _("VSG"),
                'label': '',
                'description': _("Total number of inserted entries into the cache"),
            }),
            ('vsg.dns.replaced_unexpired_entries', {
                'type': _("VSG"),
                'label': '',
                'description': _("Unexpired entries that were thrown out of cache"),
            }),
            ('vsg.dns.queries_answered_locally', {
                'type': _("VSG"),
                'label': '',
                'description': _("Number of cache hits"),
            }),
            ('vsg.dns.queries_forwarded', {
                'type': _("VSG"),
                'label': '',
                'description': _("Number of cache misses"),
            }),
            ('vsg.dns.server.queries_sent', {
                'type': _("VSG"),
                'label': '',
                'description': _("For each upstream server, the number of queries sent"),
            }),
            ('vsg.dns.server.queries_failed', {
                'type': _("VSG"),
                'label': '',
                'description': _("For each upstream server, the number of queries failed"),
            }),
        ])

    def _get_volt_meters_info(self):
        """Returns additional info for each meter

        That will be used for augmenting the Ceilometer meter
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('volt.device', {
                'type': _("VOLT"),
                'label': '',
                'description': _("Existence of olt device"),
            }),
            ('volt.device.disconnect', {
                'type': _("VOLT"),
                'label': '',
                'description': _("Olt device disconnected"),
            }),
            ('volt.device.subscriber', {
                'type': _("VOLT"),
                'label': '',
                'description': _("Existence of olt subscriber"),
            }),
            ('volt.device.subscriber.unregister', {
                'type': _("VOLT"),
                'label': '',
                'description': _("Olt subscriber unregistered"),
            }),
        ])

    def _get_sdn_meters_info(self):
        """Returns additional info for each meter

        That will be used for augmenting the Ceilometer meter
        """

        # TODO(lsmola) Unless the Ceilometer will provide the information
        # below, I need to define it as a static here. I will be joining this
        # to info that I am able to obtain from Ceilometer meters, hopefully
        # some day it will be supported all.
        return datastructures.SortedDict([
            ('switch', {
                'type': _("SDN"),
                'label': '',
                'description': _("Existence of switch"),
            }),
            ('switch.port', {
                'type': _("SDN"),
                'label': '',
                'description': _("Existence of port"),
            }),
            ('switch.port.receive.packets', {
                'type': _("SDN"),
                'label': '',
                'description': _("Packets received on port"),
            }),
            ('switch.port.transmit.packets', {
                'type': _("SDN"),
                'label': '',
                'description': _("Packets transmitted on port"),
            }),
            ('switch.port.receive.drops', {
                'type': _("SDN"),
                'label': '',
                'description': _("Drops received on port"),
            }),
            ('switch.port.transmit.drops', {
                'type': _("SDN"),
                'label': '',
                'description': _("Drops transmitted on port"),
            }),
            ('switch.port.receive.errors', {
                'type': _("SDN"),
                'label': '',
                'description': _("Errors received on port"),
            }),
            ('switch.port.transmit.errors', {
                'type': _("SDN"),
                'label': '',
                'description': _("Errors transmitted on port"),
            }),
            ('switch.flow', {
                'type': _("SDN"),
                'label': '',
                'description': _("Duration of flow"),
            }),
            ('switch.flow.packets', {
                'type': _("SDN"),
                'label': '',
                'description': _("Packets received"),
            }),
            ('switch.table', {
                'type': _("SDN"),
                'label': '',
                'description': _("Existence of table"),
            }),
            ('switch.table.active.entries', {
                'type': _("SDN"),
                'label': '',
                'description': _("Active entries in table"),
            }),
        ])

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

def calc_date_args(date_from, date_to, date_options):
    # TODO(lsmola) all timestamps should probably work with
    # current timezone. And also show the current timezone in chart.
    if date_options == "other":
        try:
            if date_from:
                date_from = pytz.utc.localize(
                    datetime.datetime.strptime(str(date_from), "%Y-%m-%d"))
            else:
                # TODO(lsmola) there should be probably the date
                # of the first sample as default, so it correctly
                # counts the time window. Though I need ordering
                # and limit of samples to obtain that.
                pass
            if date_to:
                date_to = pytz.utc.localize(
                    datetime.datetime.strptime(str(date_to), "%Y-%m-%d"))
                # It returns the beginning of the day, I want the end of
                # the day, so I add one day without a second.
                date_to = (date_to + datetime.timedelta(days=1) -
                           datetime.timedelta(seconds=1))
            else:
                date_to = timezone.now()
        except Exception:
            raise ValueError(_("The dates haven't been recognized"))
    else:
        try:
            date_to = timezone.now()
            date_from = date_to - datetime.timedelta(days=float(date_options))
        except Exception as e:
            raise e
            #raise ValueError(_("The time delta must be a number representing "
            #                   "the time span in days"))
    return date_from, date_to

class MetersList(APIView):
    method_kind = "list"
    method_name = "meters"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        tenant_ceilometer_url = getTenantCeilometerProxyURL(request.user)
        if (not tenant_ceilometer_url):
            raise XOSMissingField("Tenant ceilometer URL is missing")

        tenant_id = request.query_params.get('tenant', None)
        resource_id = request.query_params.get('resource', None)

        query = []
        if tenant_id:
            query.extend(make_query(tenant_id=tenant_id))
        if resource_id:
            query.extend(make_query(resource_id=resource_id))

        tenant_map = getTenantControllerTenantMap(request.user)
        resource_map = get_resource_map(request, ceilometer_url=tenant_ceilometer_url, query=query)
        meters = Meters(request, ceilometer_url=tenant_ceilometer_url, query=query, tenant_map=tenant_map, resource_map=resource_map)
        services = {
            _('Nova'): meters.list_nova(),
            _('Neutron'): meters.list_neutron(),
            _('VSG'): meters.list_vcpe(),
            _('VOLT'): meters.list_volt(),
            _('SDN'): meters.list_sdn(),
        }
        meters = []
        for service,smeters in services.iteritems():
             meters.extend(smeters)
        return Response(meters)

class MeterStatisticsList(APIView):
    method_kind = "list"
    method_name = "meterstatistics"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        tenant_ceilometer_url = getTenantCeilometerProxyURL(request.user)
        if (not tenant_ceilometer_url):
            raise XOSMissingField("Tenant ceilometer URL is missing")
        tenant_map = getTenantControllerTenantMap(request.user)
        
        date_options = request.query_params.get('period', 1)
        date_from = request.query_params.get('date_from', '')
        date_to = request.query_params.get('date_to', '')

        try:
            date_from, date_to = calc_date_args(date_from,
                                                date_to,
                                                date_options)
        except Exception as e:
           raise e 

        additional_query = []
        if date_from:
            additional_query.append({'field': 'timestamp',
                                     'op': 'ge',
                                     'value': date_from})
        if date_to:
            additional_query.append({'field': 'timestamp',
                                     'op': 'le',
                                     'value': date_to})

        meter_name = request.query_params.get('meter', None)
        tenant_id = request.query_params.get('tenant', None)
        resource_id = request.query_params.get('resource', None)

        query = []
        if tenant_id:
            query.extend(make_query(tenant_id=tenant_id))
        if resource_id:
            query.extend(make_query(resource_id=resource_id))

        if meter_name:
            #Statistics query for one meter
            if additional_query:
                query = query + additional_query
            statistics = statistic_list(request, meter_name,
                                        ceilometer_url=tenant_ceilometer_url, query=query, period=3600*24)
            statistic = statistics[-1]
            row = {"name": 'none',
                   "meter": meter_name,
                   "time": statistic["period_end"],
                   "value": statistic["avg"]}
            return Response(row)

        #Statistics query for all meter
        resource_map = get_resource_map(request, ceilometer_url=tenant_ceilometer_url, query=query)
        meters = Meters(request, ceilometer_url=tenant_ceilometer_url, query=query, tenant_map=tenant_map, resource_map=resource_map)
        services = {
            _('Nova'): meters.list_nova(),
            _('Neutron'): meters.list_neutron(),
            _('VSG'): meters.list_vcpe(),
            _('VOLT'): meters.list_volt(),
            _('SDN'): meters.list_sdn(),
        }
        report_rows = []
        for service,meters in services.items():
            for meter in meters:
                query = make_query(tenant_id=meter["project_id"],resource_id=meter["resource_id"])
                if additional_query:
                    query = query + additional_query
                try:
                    statistics = statistic_list(request, meter["name"],
                                        ceilometer_url=tenant_ceilometer_url, query=query, period=3600*24)
                except Exception as e:
                    logger.error('Exception during statistics query for meter %(meter)s and reason:%(reason)s' % {'meter':meter["name"], 'reason':str(e)})
                    statistics = None

                if not statistics:
                    continue
                statistic = statistics[-1]
                row = {"name": 'none',
                       "slice": meter["slice"],
                       "project_id": meter["project_id"],
                       "service": meter["service"],
                       "resource_id": meter["resource_id"],
                       "resource_name": meter["resource_name"],
                       "meter": meter["name"],
                       "description": meter["description"],
                       "category": service,
                       "time": statistic["period_end"],
                       "value": statistic["avg"],
                       "unit": meter["unit"]}
                report_rows.append(row)

        return Response(report_rows)


class MeterSamplesList(APIView):
    method_kind = "list"
    method_name = "metersamples"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        tenant_ceilometer_url = getTenantCeilometerProxyURL(request.user)
        if (not tenant_ceilometer_url):
            raise XOSMissingField("Tenant ceilometer URL is missing")
        meter_name = request.query_params.get('meter', None)
        if not meter_name:
            raise XOSMissingField("Meter name in query params is missing")
        limit = request.query_params.get('limit', 10)
        tenant_id = request.query_params.get('tenant', None)
        resource_id = request.query_params.get('resource', None)
        query = []
        if tenant_id:
            query.extend(make_query(tenant_id=tenant_id))
        if resource_id:
            query.extend(make_query(resource_id=resource_id))
        query.append({"field": "meter", "op": "eq", "value": meter_name})
        samples = sample_list(request, meter_name,
                           ceilometer_url=tenant_ceilometer_url, query=query, limit=limit) 
        if samples:
            tenant_map = getTenantControllerTenantMap(request.user)
            resource_map = get_resource_map(request, ceilometer_url=tenant_ceilometer_url)
            for sample in samples:
                 if sample["project_id"] in tenant_map.keys():
                     sample["slice"] = tenant_map[sample["project_id"]]["slice"]
                 else:
                     sample["slice"] = sample["project_id"]
                 if sample["resource_id"] in resource_map.keys():
                     sample["resource_name"] = resource_map[sample["resource_id"]]
                 else:
                     sample["resource_name"] = sample["resource_id"]
        return Response(samples)

class XOSSliceServiceList(APIView):
    method_kind = "list"
    method_name = "xos-slice-service-mapping"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        tenant_map = getTenantControllerTenantMap(request.user)
        service_map={}
        for k,v in tenant_map.iteritems():
            if not (v['service'] in service_map.keys()):
                service_map[v['service']] = {}
                service_map[v['service']]['service'] = v['service']
                service_map[v['service']]['slices'] = []
            slice_details = {'slice':v['slice'], 'project_id':k}
            service_map[v['service']]['slices'].append(slice_details)
        return Response(service_map.values())

class XOSInstanceStatisticsList(APIView):
    method_kind = "list"
    method_name = "xos-instance-statistics"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()):
            raise PermissionDenied("You must be authenticated in order to use this API")
        tenant_ceilometer_url = getTenantCeilometerProxyURL(request.user)
        if (not tenant_ceilometer_url):
            raise XOSMissingField("Tenant ceilometer URL is missing")
        instance_uuid = request.query_params.get('instance-uuid', None)
        if not instance_uuid:
            raise XOSMissingField("Instance UUID in query params is missing")
        if not Instance.objects.filter(instance_uuid=instance_uuid):
            raise XOSMissingField("XOS Instance object is missing for this uuid")
        xos_instance = Instance.objects.filter(instance_uuid=instance_uuid)[0]
        tenant_map = getTenantControllerTenantMap(request.user, xos_instance.slice)
        tenant_id = tenant_map.keys()[0]
        resource_ids = []
        resource_ids.append(instance_uuid)
        for p in xos_instance.ports.all():
            #neutron port resource id is represented in ceilometer as "nova instance-name"+"-"+"nova instance-id"+"-"+"tap"+first 11 characters of port-id
            resource_ids.append(xos_instance.instance_id+"-"+instance_uuid+"-tap"+p.port_id[:11])
        
        date_options = request.query_params.get('period', 1)
        date_from = request.query_params.get('date_from', '')
        date_to = request.query_params.get('date_to', '')

        try:
            date_from, date_to = calc_date_args(date_from,
                                                date_to,
                                                date_options)
        except Exception as e:
           raise e 

        additional_query = []
        if date_from:
            additional_query.append({'field': 'timestamp',
                                     'op': 'ge',
                                     'value': date_from})
        if date_to:
            additional_query.append({'field': 'timestamp',
                                     'op': 'le',
                                     'value': date_to})

        report_rows = []
        for resource_id in resource_ids:
            query = []
            if tenant_id:
                query.extend(make_query(tenant_id=tenant_id))
            if resource_id:
                query.extend(make_query(resource_id=resource_id))

            #Statistics query for all meter
            resource_map = get_resource_map(request, ceilometer_url=tenant_ceilometer_url, query=query)
            meters = Meters(request, ceilometer_url=tenant_ceilometer_url, query=query, tenant_map=tenant_map, resource_map=resource_map)
            exclude_nova_meters_info = [ "instance", "instance:<type>", "disk.read.requests", "disk.write.requests",
                "disk.read.bytes", "disk.write.bytes", "disk.read.requests.rate", "disk.write.requests.rate", "disk.read.bytes.rate",
                "disk.write.bytes.rate", "disk.root.size", "disk.ephemeral.size"]
            exclude_neutron_meters_info = [ 'network.create', 'network.update', 'subnet.create',
                'subnet.update', 'port.create', 'port.update', 'router.create', 'router.update',
                'ip.floating.create', 'ip.floating.update']
            services = {
                _('Nova'): meters.list_nova(except_meters=exclude_nova_meters_info),
                _('Neutron'): meters.list_neutron(except_meters=exclude_neutron_meters_info),
                _('VSG'): meters.list_vcpe(),
                _('VOLT'): meters.list_volt(),
                _('SDN'): meters.list_sdn(),
            }
            for service,meters in services.items():
                for meter in meters:
                    query = make_query(tenant_id=meter["project_id"],resource_id=meter["resource_id"])
                    if additional_query:
                        query = query + additional_query
                    try:
                        statistics = statistic_list(request, meter["name"],
                                            ceilometer_url=tenant_ceilometer_url, query=query, period=3600*24)
                    except Exception as e:
                        logger.error('Exception during statistics query for meter %(meter)s and reason:%(reason)s' % {'meter':meter["name"], 'reason':str(e)})
                        statistics = None

                    if not statistics:
                        continue
                    statistic = statistics[-1]
                    row = {"name": 'none',
                           "slice": meter["slice"],
                           "project_id": meter["project_id"],
                           "service": meter["service"],
                           "resource_id": meter["resource_id"],
                           "resource_name": meter["resource_name"],
                           "meter": meter["name"],
                           "description": meter["description"],
                           "category": service,
                           "time": statistic["period_end"],
                           "value": statistic["avg"],
                           "unit": meter["unit"]}
                    report_rows.append(row)

        return Response(report_rows)

class ServiceAdjustScale(APIView):
    method_kind = "list"
    method_name = "serviceadjustscale"

    def get(self, request, format=None):
        if (not request.user.is_authenticated()) or (not request.user.is_admin):
            raise PermissionDenied("You must be authenticated admin user in order to use this API")
        service = request.query_params.get('service', None)
        slice_hint = request.query_params.get('slice_hint', None)
        scale = request.query_params.get('scale', None)
        if not service or not slice_hint or not scale:
            raise XOSMissingField("Mandatory fields missing")
        services = Service.select_by_user(request.user)
        logger.info('SRIKANTH: Services for this user %(services)s' % {'services':services})
        if not services or (not services.get(name=service)):
            raise XOSMissingField("Service not found")
        service = services.get(name=service)
        service.adjust_scale(slice_hint, int(scale))
        return Response("Success")
