class Meta:
    app_label = "core"
    ordering = ('order', 'name')

def __init__(self, *args, **kwargs):
    super(Flavor, self).__init__(*args, **kwargs)
    self.no_sync=True

