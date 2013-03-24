from PLC.Roles import Roles
from model import Role

class RoleImporter:

    def __init__(self, importer):
        self.importer = importer
        self.roles = {}

    def run(self):
        roles = self.importer.api.GetRoles()
        db_roles =  Role.objects.all()
        db_roles_list = [db_role['name'] for db_role in db_roles]
        for role in roles:
            if role['name'] not in db_roles_list:
                new_role = Role(name=role['name'])
                new_role.save()
            self.roles[role['role_id']] = role

          

