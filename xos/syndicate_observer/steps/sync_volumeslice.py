#!/usr/bin/env python

import os
import sys
import base64
import traceback

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
from core.models import Service, Slice

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

from syndicate_storage.models import VolumeSlice,VolumeAccessRight,Volume

# syndicatelib will be in stes/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

import syndicatelib


class SyncVolumeSlice(SyncStep):
    provides=[VolumeSlice]
    requested_interval=0

    def __init__(self, **args):
        SyncStep.__init__(self, **args)

    def sync_record(self, vs):
        
        logger.info("Sync VolumeSlice for (%s, %s)" % (vs.volume_id.name, vs.slice_id.name))
        
        # extract arguments...
        user_email = vs.slice_id.creator.email
        slice_name = vs.slice_id.name
        volume_name = vs.volume_id.name
        syndicate_caps = syndicatelib.opencloud_caps_to_syndicate_caps( vs.cap_read_data, vs.cap_write_data, vs.cap_host_data )
        RG_port = vs.RG_portnum
        UG_port = vs.UG_portnum
        slice_secret = None
        
        config = syndicatelib.get_config()
        try:
           observer_secret = config.SYNDICATE_OPENCLOUD_SECRET
           RG_closure = config.SYNDICATE_RG_CLOSURE
           observer_pkey_path = config.SYNDICATE_PRIVATE_KEY
           syndicate_url = config.SYNDICATE_SMI_URL
           
        except Exception, e:
           traceback.print_exc()
           logger.error("syndicatelib config is missing one or more of the following: SYNDICATE_OPENCLOUD_SECRET, SYNDICATE_RG_CLOSURE, SYNDICATE_PRIVATE_KEY, SYNDICATE_SMI_URL")
           raise e
            
        # get secrets...
        try:
           observer_pkey_pem = syndicatelib.get_private_key_pem( observer_pkey_path )
           assert observer_pkey_pem is not None, "Failed to load Observer private key"
           
           # get/create the slice secret
           slice_secret = syndicatelib.get_or_create_slice_secret( observer_pkey_pem, slice_name )    
           assert slice_secret is not None, "Failed to get or create slice secret for %s" % slice_name
           
        except Exception, e:
           traceback.print_exc()
           logger.error("Failed to load secret credentials")
           raise e
        
        # make sure there's a slice-controlled Syndicate user account for the slice owner
        slice_principal_id = syndicatelib.make_slice_principal_id( user_email, slice_name )
        
        try:
            rc, user = syndicatelib.ensure_principal_exists( slice_principal_id, observer_secret, is_admin=False, max_UGs=1100, max_RGs=1 )
            assert rc is True, "Failed to ensure principal %s exists (rc = %s,%s)" % (slice_principal_id, rc, user)
        except Exception, e:
            traceback.print_exc()
            logger.error('Failed to ensure slice user %s exists' % slice_principal_id)
            raise e
            
        # grant the slice-owning user the ability to provision UGs in this Volume, and also provision for the user the (single) RG the slice will instantiate in each VM.
        try:
            rc = syndicatelib.setup_volume_access( slice_principal_id, volume_name, syndicate_caps, RG_port, observer_secret, RG_closure=RG_closure )
            assert rc is True, "Failed to set up Volume access for slice %s in %s" % (slice_principal_id, volume_name)
            
        except Exception, e:
            traceback.print_exc()
            logger.error("Failed to set up Volume access for slice %s in %s" % (slice_principal_id, volume_name))
            raise e
            
        # generate and save slice credentials....
        try:
            slice_cred = syndicatelib.save_slice_credentials( observer_pkey_pem, syndicate_url, slice_principal_id, volume_name, slice_name, observer_secret, slice_secret, UG_port, existing_user=user )
            assert slice_cred is not None, "Failed to generate slice credential for %s in %s" % (slice_principal_id, volume_name )
                
        except Exception, e:
            traceback.print_exc()
            logger.error("Failed to generate slice credential for %s in %s" % (slice_principal_id, volume_name))
            raise e
             
        # ... and push them all out.
        try:
            rc = syndicatelib.push_credentials_to_slice( slice_name, slice_cred )
            assert rc is True, "Failed to push credentials to slice %s for volume %s" % (slice_name, volume_name)
               
        except Exception, e:
            traceback.print_exc()
            logger.error("Failed to push slice credentials to %s for volume %s" % (slice_name, volume_name))
            raise e
        
        return True
    
    # This method will simply cause the object to be purged from OpenCloud
    def delete_record(self, volume_slice):
        pass


if __name__ == "__main__":
    sv = SyncVolumeSlice()

    # first, set all VolumeSlice to not-enacted so we can test 
    for v in VolumeSlice.objects.all():
       v.enacted = None
       v.save()

    # NOTE: for resetting only 
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
       sys.exit(0)

    recs = sv.fetch_pending()

    for rec in recs:
        if rec.slice_id.creator is None:
           print "Ignoring slice %s, since it has no creator" % (rec.slice_id)
           continue

        sv.sync_record( rec )

