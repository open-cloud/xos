
class UserImporter:

    def __init__(self, api):
        self.api = api
        self.users = {}

    def run(self):
        users = self.api.GetPersons()

    def save_site_privs(self, user):
        # update site roles
        pass

    def save_slice_privs(self, user):
        # update slice roles
        pass
          

