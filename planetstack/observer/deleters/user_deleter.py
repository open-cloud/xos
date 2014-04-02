from core.models import User, UserDeployments
from observer.deleter import Deleter

class UserDeleter(Deleter):
    model='User'

    def call(self, pk):
        user = User.objects.get(pk=pk)
        user_deployments = UserDeployments.objects.filter(user=user)
        for user_deployment in user_deployments:
            if user_deployment.user.kuser_id:
                driver = self.driver.admin_driver(deployment=user_deployment.deployment.name)
                driver.delete_user(user_deployment.user.kuser_id)
            user_deployment.delete()
        user.delete()
