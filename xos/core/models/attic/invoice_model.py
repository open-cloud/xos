@property
def amount(self):
    return str(self.charges.all().aggregate(Sum('amount'))["amount__sum"])

def __unicode__(self):  return u'%s-%s' % (self.account.site.name, str(self.date))
