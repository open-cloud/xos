#!/usr/bin/env python

import os
import sys
import traceback
import base64

if __name__ == "__main__":
    # for testing 
    if os.getenv("OPENCLOUD_PYTHONPATH"):
        sys.path.append( os.getenv("OPENCLOUD_PYTHONPATH") )
    else:
        print >> sys.stderr, "No OPENCLOUD_PYTHONPATH variable set.  Assuming that OpenCloud is in PYTHONPATH"
 
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")


from django.db.models import F, Q
from xos.config import Config
from observer.syncstep import SyncStep
from core.models import Service
from syndicate_storage.models import Volume

import logging
from logging import Logger
logging.basicConfig( format='[%(levelname)s] [%(module)s:%(lineno)d] %(message)s' )
logger = logging.getLogger()
logger.setLevel( logging.INFO )

# point to planetstack
if __name__ != "__main__": 
    if os.getenv("OPENCLOUD_PYTHONPATH") is not None:
        sys.path.insert(0, os.getenv("OPENCLOUD_PYTHONPATH"))
    else:
        logger.warning("No OPENCLOUD_PYTHONPATH set; assuming your PYTHONPATH works")

# syndicatelib will be in stes/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

import syndicatelib


class SyncVolume(SyncStep):
    provides=[Volume]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)

    def sync_record(self, volume):
        """
        Synchronize a Volume record with Syndicate.
        """
        
        logger.info( "Sync Volume = %s\n\n" % volume.name )
    
        user_email = volume.owner_id.email
        config = syndicatelib.get_config()
        
        volume_principal_id = syndicatelib.make_volume_principal_id( user_email, volume.name )

        # get the observer secret 
        try:
            observer_secret = config.SYNDICATE_OPENCLOUD_SECRET
        except Exception, e:
            traceback.print_exc()
            logger.error("config is missing SYNDICATE_OPENCLOUD_SECRET")
            raise e

        # volume owner must exist as a Syndicate user...
        try:
            rc, user = syndicatelib.ensure_principal_exists( volume_principal_id, observer_secret, is_admin=False, max_UGs=1100, max_RGs=1)
            assert rc == True, "Failed to create or read volume principal '%s'" % volume_principal_id
        except Exception, e:
            traceback.print_exc()
            logger.error("Failed to ensure principal '%s' exists" % volume_principal_id )
            raise e

        # volume must exist 
        
        # create or update the Volume
        try:
            new_volume = syndicatelib.ensure_volume_exists( volume_principal_id, volume, user=user )
        except Exception, e:
            traceback.print_exc()
            logger.error("Failed to ensure volume '%s' exists" % volume.name )
            raise e
           
        # did we create the Volume?
        if new_volume is not None:
            # we're good
            pass 
             
        # otherwise, just update it 
        else:
            try:
                rc = syndicatelib.update_volume( volume )
            except Exception, e:
                traceback.print_exc()
                logger.error("Failed to update volume '%s', exception = %s" % (volume.name, e.message))
                raise e
                    
        return True
    
    def delete_record(self, volume):
        try:
            volume_name = volume.name
            syndicatelib.ensure_volume_absent( volume_name )
        except Exception, e:
            traceback.print_exc()
            logger.exception("Failed to erase volume '%s'" % volume_name)
            raise e





if __name__ == "__main__":
    sv = SyncVolume()


    # first, set all volumes to not-enacted so we can test 
    for v in Volume.objects.all():
       v.enacted = None
       v.save()
    
    # NOTE: for resetting only 
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
       sys.exit(0)

    recs = sv.fetch_pending()

    for rec in recs:
        rc = sv.sync_record( rec )
        if not rc:
          print "\n\nFailed to sync %s\n\n" % (rec.name)

