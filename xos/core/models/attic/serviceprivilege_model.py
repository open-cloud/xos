class Meta:
    unique_together = ('user', 'service', 'role')

@classmethod
def select_by_user(cls, user):
    if user.is_admin:
        qs = cls.objects.all()
    else:
        qs = cls.objects.filter(user=user)
    return qs
