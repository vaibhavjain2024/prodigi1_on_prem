from .action import Action
from ..enums import ActionTypes,Scopes, ReadLevels

class ProvisionAction(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.PROVISION)
        
    def is_permitted(self, scope):
        if self.scope[Scopes.PERMITTED] :
            if( self.scope[Scopes.PROVISIONING_TYPE] == ["*"] \
                or scope[Scopes.PROVISIONING_TYPE] in self.scope[Scopes.PROVISIONING_TYPE] ) :
                return True
        return False

    def check_role_permission(self,scope):
        if self.scope[Scopes.PERMITTED] :
            if( self.scope[Scopes.PROVISIONING_TYPE] == ["*"] \
                or scope[Scopes.PROVISIONING_TYPE] in self.scope[Scopes.PROVISIONING_TYPE] ) :
                return True
        return False

                
    def set_level(self, scope_level):
        self.set_scope[Scopes.LEVEL] = scope_level

