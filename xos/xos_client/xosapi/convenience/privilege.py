from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperPrivilege(ORMWrapper):
    pass
    
register_convenience_wrapper("Privilege", ORMWrapperPrivilege)
