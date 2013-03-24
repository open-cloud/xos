from PLC.Slices import Slices
from models import Slice

class SliceImporter:

    def __init__(self, importer):
        self.importer = importer
        self.slices = {}

    def run(self):
        slices = Slices(self.importer.api)
        db_slices = Slice.objects.all()
        slice_names = [s['name'] for s in db_slices]
        for slice in slices:
            if slice['name'] not in slice_names:
                new_slices = Slice(name=slice['name'],
                                   instantiation=slice['instantiation'],
                                   omf_friendly = False,
                                   description = slice['description'],
                                   slice_url = slice['url'])
                new_slice.save();
            self.slices[slice['slice_id']] = slice

          

