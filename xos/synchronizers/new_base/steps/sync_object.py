from synchronizers.new_base.syncstep import *

class SyncObject(SyncStep):
    provides=[] # Caller fills this in
    requested_interval=0
    observes=[] # Caller fills this in

    def sync_record(self, r):
        raise DeferredException('Waiting for Service dependency: %r'%r)
