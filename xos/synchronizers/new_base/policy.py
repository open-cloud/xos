""" policy.py

    Base Classes for Model Policies
"""

from xos.logger import Logger, logging

class Policy(object):
    """ An XOS Model Policy

        Set the class member model_name to the name of the model that this policy will act on.

        The following functions will be invoked if they are defined:

            handle_create ... called when a model is created
            handle_update ... called when a model is updated
            handle_delete ... called when a model is deleted
    """

    def __init__(self):
        self.logger = Logger(level=logging.DEBUG)

