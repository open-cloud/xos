from core.models import User
from observer.deleter import Deleter

class UserDeleter(Deleter):
    model='User'

    def call(self, pk):
        user = User.objects.get(pk=pk)
        if user.kuser_id:
            self.driver.delete_user(user.kuser_id)
        user.delete()
