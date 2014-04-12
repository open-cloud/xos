from core.models import User, UserDeployments
from observer.deleter import Deleter

class UserDeploymentDeleter(Deleter):
    model='UserDeployment'

    def call(self, pk):
        user_deployment = UserDeployments.objects.get(pk=pk)
        if user_deployment.user.kuser_id:
            driver = self.driver.admin_driver(deployment=user_deployment.deployment.name)
            driver.delete_user(user_deployment.user.kuser_id)
        user_deployment.delete()
