from .action import Action
from ..enums import ActionTypes,Scopes, ReadLevels

class ReadAction(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.READ)
        
    def is_permitted(self, scope):
        return self.scope[Scopes.LEVEL]
        # return  self.scope[Scopes.LEVEL] <= scope[Scopes.LEVEL]
    
    def check_role_permission(self,scope):
        
        return  self.scope[Scopes.LEVEL] <= scope[Scopes.LEVEL]
            
    def set_level(self, scope_level):
        self.set_scope[Scopes.LEVEL] = scope_level

