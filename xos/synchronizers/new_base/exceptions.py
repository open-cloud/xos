class SynchronizerException(Exception):
    pass

class SynchronizerProgrammingError(SynchronizerException): 
    pass

class SynchronizerConfigurationError(SynchronizerException):
    pass
