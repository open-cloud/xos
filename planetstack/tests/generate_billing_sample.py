"""
    Generates billing sample data
"""

import datetime
import os
import operator
import pytz
import json
import random
import sys
import time

# The granularity at which the charge collection system collects charges. Once
# per hour makes for a very slow UI, so I upped it to once per 8 hours.
CHARGE_HOURS = 8

MINUTE_SECONDS = 60
HOUR_SECONDS = MINUTE_SECONDS * 60
DAY_SECONDS = HOUR_SECONDS * 24
MONTH_SECONDS = DAY_SECONDS * 30


sys.path.append("/opt/planetstack")
#sys.path.append("/home/smbaker/projects/vicci/plstackapi/planetstack")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
#from openstack.manager import OpenStackManager
from core.models import Slice, Sliver, ServiceClass, Reservation, Tag, Network, User, Node, Image, Deployment, Site, NetworkTemplate, NetworkSlice
from core.models import Invoice, Charge, Account, UsableObject, Payment

def delete_all(model):
   for item in model.objects.all():
       item.delete()

def get_usable_object(name):
   objs = UsableObject.objects.filter(name=name)
   if objs:
       return objs[0]
   obj = UsableObject(name=name)
   obj.save()
   return obj

def generate_invoice(account, batch):
   invoice = Invoice(date=batch[-1].date, account=account)
   invoice.save()
   for charge in batch:
       charge.invoice = invoice
       charge.state = "invoiced"
       charge.save()

def generate_invoices(account):
   invoices = sorted(Invoice.objects.filter(account=account), key=operator.attrgetter('date'))
   charges = sorted(Charge.objects.filter(account=account, state="pending"), key=operator.attrgetter('date'))

   if invoices:
       latest_invoice_date = invoices[-1].date()
   else:
       latest_invoice_date = None

   batch = []
   last_week = 0
   for charge in charges:
       # check to see if we crossed a week boundary. If we did, then generate
       # an invoice for the last week's batch of charges
       week = charge.date.isocalendar()[1]
       if (week != last_week) and (batch):
           generate_invoice(account, batch)
           batch = []
           last_week = week
       batch.append(charge)

   # we might still have last week's data batched up, and no data for this week
   # if so, invoice the batch
   this_week = datetime.datetime.now().isocalendar()[1]
   if (this_week != last_week) and (batch):
       generate_invoice(account, batch)

def generate_payments(account):
    invoices = Invoice.objects.filter(account=account)
    for invoice in invoices:
        # let's be optomistic and assume everyone pays exactly two weeks after
        # receiving an invoice
        payment_time = int(invoice.date.strftime("%s")) + 14 * DAY_SECONDS
        if payment_time < time.time():
             payment_time = datetime.datetime.utcfromtimestamp(payment_time).replace(tzinfo=pytz.utc)
             payment = Payment(account=account, amount=invoice.amount, date=payment_time)
             payment.save()

print "deleting old stuff"

delete_all(Invoice)
delete_all(Charge)
delete_all(Payment)
delete_all(Account)
delete_all(UsableObject)

print "creating accounts"

for site in Site.objects.all():
    # only create accounts for sites where some slices exist
    if len(site.slices.all()) > 0:
        account = Account(site=site)
        account.save()

print "generating charges"

for slice in Slice.objects.all():
    site = slice.site
    account = site.accounts.all()[0]
    serviceClass =slice.serviceClass

    if not (slice.name in ["DnsRedir", "DnsDemux", "HyperCache", "Hadoop", "Owl", "Stork", "Syndicate", "test-slice-1", "test-slice-2", "test", "test2"]):
        continue

    print "   generating charges for", slice.name

    now = int(time.time())/HOUR_SECONDS*HOUR_SECONDS

    charge_kind=None
    for resource in slice.serviceClass.resources.all():
        if resource.name == "numberCores":
            charge_kind = "reservation"
            cost = resource.cost
        elif (charge_kind==None) and (resource.name == "cycles") or (resource.name == "Cycles"):
            charge_kind = "besteffort"
            cost = resource.cost

    if not charge_kind:
        print "failed to find resource for", slice.serviceClass
        continue

    for sliver in slice.slivers.all()[:4]:    # only do up to 4 slivers; it's way too much data otherwise
        hostname = sliver.node.name
        for i in range(now-MONTH_SECONDS, now, CHARGE_HOURS*HOUR_SECONDS):
            if charge_kind == "besteffort":
                core_hours = random.randint(20,60)/100.0
            else:
                core_hours = 1

            core_hours = core_hours * CHARGE_HOURS

            amount = float(core_hours * cost) / 100.0

            object = get_usable_object(hostname)

            date = datetime.datetime.utcfromtimestamp(i).replace(tzinfo=pytz.utc)

            charge = Charge(account=account, slice=slice, kind=charge_kind, state="pending", date=date, object=object, coreHours=core_hours, amount=amount)
            charge.save()

print "doing invoices and payments"

for account in Account.objects.all():
    generate_invoices(account)
    generate_payments(account)



