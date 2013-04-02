from plstackapi.core.models import Site

class SiteImporter:

    def __init__(self, api):
        self.api = api
        self.remote_sites = {}
        self.local_sites = {}

    def run(self):
        db_sites = Site.objects.all()
        for db_site in db_sites:
            self.local_sites[db_site.login_base] = db_site

        sites = self.api.GetSites()
        for site in sites:
            self.remote_sites[site['site_id']] = site 
            if site['login_base'] not in self.local_sites:
                new_site = Site(name=site['name'],
                                site_url=site['url'],
                                enabled=site['enabled'],
                                longitude=site['longitude'],
                                latitude=site['latitude'],
                                is_public=site['is_public'],
                                abbreviated_name=site['abbreviated_name'])
                new_site.save()
                self.local_sites[new_site.login_base] = new_site
