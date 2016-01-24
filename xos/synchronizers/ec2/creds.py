from core.models import *

def get_creds(user=None, slice=None, site=None, deployment=None):
    if (not user or not site):
        raise Exception('User and Site have to be in context to use EC2')

    cred = UserCredential.objects.filter(user=user)
    if (not cred):
        cred = SiteCredential.objects.filter(site=site)
        
    if (cred):
        env = 'AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s'%(cred.key_id, cred.enc_value) 
    else:
        env = ''

    return env
