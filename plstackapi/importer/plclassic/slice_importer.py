from plstackapi.core.models import Slice

class SliceImporter:

    def __init__(self, api):
        self.api = api
        self.remote_slices = {}
        self.local_slices = {}

    def run(self, remote_sites={}, local_sites={}):
        if not remote_sites:
            sites = self.api.GetSites({'peer_id': None})
            for site in sites:
                remote_sites[site['site_id']] = site
        

        if not local_sites:
            from plstackapi.core.models import Site
            sites = Site.objects.all()
            for site in sites:
                local_sites[site.login_base] = site            

        db_slices = Slice.objects.all()
        for db_slice in db_slices:
            self.local_slices[db_slice.name] = db_slice
        print "%s local slices" % len(db_slices)

        slices = self.api.GetSlices({'peer_id': None})
        print "%s remote slices" % len(slices)
        count = 0 
        for slice in slices:
            self.remote_slices[slice['slice_id']] = slice
            if slice['name'] not in self.local_slices:
                site = local_sites[remote_sites[slice['site_id']]['login_base']]
                new_slice = Slice(name=slice['name'],
                                   omf_friendly = False,
                                   description = slice['description'],
                                   slice_url = slice['url'],
                                   site = site)
                new_slice.save()
                count += 1
                self.local_slices[new_slice.name] = new_slice
        print "Imported %s slices" % count

          

