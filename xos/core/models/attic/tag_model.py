def can_update(self, user):
    return user.can_update_root()

@classmethod
def select_by_content_object(cls, obj):
    return cls.objects.filter(content_type=obj.get_content_type_key(), object_id=obj.id)

@staticmethod
def select_by_user(user):
    return Tag.objects.all()
