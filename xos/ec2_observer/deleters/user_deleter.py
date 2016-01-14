from core.models import User, UserDeployments
from synchronizers.base.deleter import Deleter
from synchronizers.base.deleters.user_deployment_deleter import UserDeploymentsDeleter

class UserDeleter(Deleter):
    model='User'

    def call(self, pk):
        user = User.objects.get(pk=pk)
        user_deployment_deleter = UserDeploymentsDeleter()
        for user_deployment in UserDeployments.objects.filter(user=user):
            user_deployment_deleter(user_deployment.id)
        user.delete()
