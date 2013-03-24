from PLC.Persons import Persons
from models import User

class UserImporter:

    def __init__(self, importer):
        self.importer = importer
        self.users = {}

    def run(self):
        users = Persons(self.importer.api)
        db_users = User.objects.all()
        usernames = [u['email'] for u in db_users]     
        for user in users:
            if user['email'] not in usernames:
                new_user = User(firstname=user['first_name'],
                                lastname=user['last_name'],
                                email=user['email'],
                                phone=user['phone'],
                                user_url = user['url'],
                                site = user['sites_ids'][0])
                new_user.save()
                self.save_site_privs(user) 
                self.save_slice_privs(user) 
            self.users[user['person_id']] = user

    def save_site_privs(self, user):
        # update site roles
        pass

    def save_slice_privs(self, user):
        # update slice roles
        pass
          

