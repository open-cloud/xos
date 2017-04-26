@property
def enacted(self):
    return None

@enacted.setter
def enacted(self, value):
    pass # Ignore sets, Diag objects are always pending.
