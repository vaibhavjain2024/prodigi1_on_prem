from .action import Action
from ..enums import ActionTypes,Scopes, ReadLevels

class UpdateAction(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.UPDATE)
        
    def is_permitted(self, scope):
        if self.scope[Scopes.PERMITTED]:
            return self.scope[Scopes.LEVEL]
        else :
            return False

    def check_role_permission(self, scope):
        if self.scope[Scopes.PERMITTED]:
            return self.scope[Scopes.LEVEL] <= scope[Scopes.LEVEL]
        else :
            return False

    def set_level(self, scope_level):
        self.set_scope[Scopes.LEVEL] = scope_level

    def allow_write(self):
        self.scope[Scopes.PERMITTED] = True
    
    def disallow_write(self):
        self.scope[Scopes.PERMITTED] = False