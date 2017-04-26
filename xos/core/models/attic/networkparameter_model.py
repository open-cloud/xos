content_object = GenericForeignKey('content_type', 'object_id')

def __unicode__(self):
    return self.parameter.name

