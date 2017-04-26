def __unicode__(self):  return u'%s to %s' % (self.startTime, self.endTime)

@property
def endTime(self):
    return self.startTime + datetime.timedelta(hours=self.duration)

def can_update(self, user):
    return user.can_update_slice(self.slice)

@staticmethod
def select_by_user(user):
    if user.is_admin:
        qs = Reservation.objects.all()
    else:
        slice_ids = [s.id for s in Slice.select_by_user(user)]
        qs = Reservation.objects.filter(id__in=slice_ids)
    return qs
