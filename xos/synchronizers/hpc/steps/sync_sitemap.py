import os
import sys
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from core.models import Service
from services.hpc.models import ServiceProvider, ContentProvider, CDNPrefix, SiteMap
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

from hpclib import HpcLibrary

logger = Logger(level=logging.INFO)

class SyncSiteMap(SyncStep, HpcLibrary):
    provides=[SiteMap]
    observes=SiteMap
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)
        HpcLibrary.__init__(self)

    def filter_hpc_service(self, objs):
        hpcService = self.get_hpc_service()

        filtered_objs = []
        for x in objs:
            if ((x.hpcService == hpcService) or
               ((x.serviceProvider != None) and (x.serviceProvider.hpcService == hpcService)) or
               ((x.contentProvider != None) and (x.contentProvider.serviceProvider.hpcService == hpcService)) or
               ((x.cdnPrefix!= None) and (x.cdnPrefix.contentProvider.serviceProvider.hpcService == hpcService))):
                filtered_objs.append(x)

        return filtered_objs

    def fetch_pending(self, deleted):
        return self.filter_hpc_service(SyncStep.fetch_pending(self, deleted))

    def consistency_check(self):
        # set to true if something changed
        result=False

        # sanity check to make sure our PS objects have CMI objects behind them
        all_map_ids = [x["map_id"] for x in self.client.onev.ListAll("Map")]
        for map in SiteMap.objects.all():
            if (map.map_id is not None) and (map.map_id not in all_map_ids):
                logger.info("Map %s was not found on CMI" % map.map_id,extra=map.tologdict())
                map.map_id=None
                map.save()
                result = True

        return result

    def update_bind(self, map, map_dict, field_name, to_name, ids):
        for id in ids:
            if (not id in map_dict.get(field_name, [])):
                print "Bind Map", map.map_id, "to", to_name, id
                self.client.onev.Bind("Map", map.map_id, to_name, id)

        for id in map_dict.get(field_name, []):
            if (not id in ids):
                print "Unbind Map", map.map_id, "from", to_name, id
                self.client.onev.UnBind("map", map.map_id, to_name, id)

    def sync_record(self, map):
        logger.info("sync'ing SiteMap %s" % str(map),extra=map.tologdict())

        if not map.map:
            # no contents
            return

        content = map.map.read()

        map_dict = {"name": map.name, "type": "site", "content": content}

        cdn_prefix_ids=[]
        service_provider_ids=[]
        content_provider_ids=[]

        if (map.contentProvider):
            if not map.contentProvider.content_provider_id:
                raise Exception("Map %s links to a contentProvider with no id" % map.name)
            conent_provider_ids = [map.contentProvider.content_provider_id]

        if (map.serviceProvider):
            if not map.serviceProvider.service_provider_id:
                raise Exception("Map %s links to a serviceProvider with no id" % map.name)
            service_provider_ids = [map.serviceProvider.service_provider_id]

        if (map.cdnPrefix):
            if not map.cdnPrefix.cdn_prefix_id:
                raise Exception("Map %s links to a cdnPrefix with no id" % map.name)
            cdn_prefix_ids = [map.cdnPrefix.cdn_prefix_id]

        if not map.map_id:
            print "Create Map", map_dict
            id = self.client.onev.Create("Map", map_dict)
            map.map_id = id
        else:
            print "Update Map", map_dict
            # these things we probably cannot update
            del map_dict["name"]
            self.client.onev.Update("Map", map.map_id, map_dict)

        cmi_map_dict = self.client.onev.Read("Map", map.map_id)

        self.update_bind(map, cmi_map_dict, "cdn_prefix_ids", "CDNPrefix", cdn_prefix_ids)

        map.save()

    def delete_record(self, m):
        if m.map_id is not None:
            self.client.onev.Delete("Map", m.map_id)
