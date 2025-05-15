from .action import Action
from ..enums import ActionTypes,Scopes, ReadLevels

class AdminAction(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.ADMIN)
        
    def is_permitted(self, scope):
        return self.scope[Scopes.PERMITTED]
        # return  self.scope[Scopes.LEVEL] <= scope[Scopes.LEVEL]
    
    def check_role_permission(self,scope):
        
        return  self.scope[Scopes.PERMITTED] <= scope[Scopes.PERMITTED]
            
    def set_level(self, scope_level):
        self.set_scope[Scopes.PERMITTED] = scope_level

