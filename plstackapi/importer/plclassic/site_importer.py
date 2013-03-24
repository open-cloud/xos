from PLC.Sites import Sites
from models import Site

class SiteImporter:

    def __init__(self, importer):
        self.importer = importer
        self.sites = {}

    def run(self):
        sites = Sites(self.importer.api)
        db_sites = Site.objects.all()
        db_site_names = [s['login_base'] for s in db_sites]         
        for site in sites:
            if site['login_base'] not in db_site_names:
                new_site = Site(name=site['name'],
                                site_url=site['url'],
                                enabled=site['enabled'],
                                longitude=site['longitude'],
                                latitude=site['latitude'],
                                is_public=site['is_public'],
                                abbreviated_name=site['abbreviated_name'])
                new_site.save()
            self.sites[site['site_id']] = site

          

