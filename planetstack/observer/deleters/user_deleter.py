from core.models import User, UserDeployments
from observer.deleter import Deleter
from observer.deleters.user_deployment_deleter import UserDeploymentDeleter

class UserDeleter(Deleter):
    model='User'

    def call(self, pk):
        user = User.objects.get(pk=pk)
        user_deployment_deleter = UserDeploymentDeleter()
        for user_deployment in UserDeployments.objects.filter(user=user):
            user_deployment_deleter(user_deployment.id)
        user.delete()
