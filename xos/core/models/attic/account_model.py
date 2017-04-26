@property
def total_invoices(self):
    # Since the amount of an invoice is the sum of it's charges, we can
    # compute the sum of the invoices by summing all charges where
    # charge.invoice != Null.
    x=self.charges.filter(invoice__isnull=False).aggregate(Sum('amount'))["amount__sum"]
    if (x==None):
        return 0.0
    return x

@property
def total_payments(self):
    x=self.payments.all().aggregate(Sum('amount'))["amount__sum"]
    if (x==None):
        return 0.0
    return x

@property
def balance_due(self):
    return self.total_invoices - self.total_payments

def __unicode__(self):  return u'%s' % (self.site.name)

