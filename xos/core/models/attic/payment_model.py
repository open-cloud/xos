def __unicode__(self): return u'%s-%0.2f-%s' % (self.account.site.name, self.amount, str(self.date))
