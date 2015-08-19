import datetime
import os
import socket
from django.db import models
from core.models import PlCoreBase, Site, Slice, Instance, Deployment
from core.models.plcorebase import StrippedCharField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Sum
from django.utils import timezone

class Account(PlCoreBase):
    site = models.ForeignKey(Site, related_name="accounts", help_text="Site for this account")

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

class Invoice(PlCoreBase):
    date = models.DateTimeField()
    account = models.ForeignKey(Account, related_name="invoices")

    @property
    def amount(self):
        return str(self.charges.all().aggregate(Sum('amount'))["amount__sum"])

    def __unicode__(self):  return u'%s-%s' % (self.account.site.name, str(self.date))

class UsableObject(PlCoreBase):
    name = StrippedCharField(max_length=1024)

    def __unicode__(self):  return u'%s' % (self.name)

class Payment(PlCoreBase):
    account = models.ForeignKey(Account, related_name="payments")
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(default=timezone.now)

    def __unicode__(self): return u'%s-%0.2f-%s' % (self.account.site.name, self.amount, str(self.date))

class Charge(PlCoreBase):
    KIND_CHOICES = (('besteffort', 'besteffort'), ('reservation', 'reservation'), ('monthlyfee', 'monthlyfee'))
    STATE_CHOICES = (('pending', 'pending'), ('invoiced', 'invoiced'))

    account = models.ForeignKey(Account, related_name="charges")
    slice = models.ForeignKey(Slice, related_name="charges", null=True, blank=True)
    kind = StrippedCharField(max_length=30, choices=KIND_CHOICES, default="besteffort")
    state = StrippedCharField(max_length=30, choices=STATE_CHOICES, default="pending")
    date = models.DateTimeField()
    object = models.ForeignKey(UsableObject)
    amount = models.FloatField(default=0.0)
    coreHours = models.FloatField(default=0.0)
    invoice = models.ForeignKey(Invoice, blank=True, null=True, related_name="charges")

    def __unicode__(self):  return u'%s-%0.2f-%s' % (self.account.site.name, self.amount, str(self.date))




