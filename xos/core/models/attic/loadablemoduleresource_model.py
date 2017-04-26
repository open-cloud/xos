def __unicode__(self): return u'%s' % (self.name)

@property
def full_url(self):
    if self.loadable_module and self.loadable_module.base_url:
        return urlparse.urljoin(self.loadable_module.base_url, self.url)
    else:
        return self.url
