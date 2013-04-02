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
        print "%s local sites" % len(db_sites)

        sites = self.api.GetSites()
        print "%s remote sites" %s len(sites))
        count = 0
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
                count += 1
                self.local_sites[new_site.login_base] = new_site
        print "imported %s sites" % count
