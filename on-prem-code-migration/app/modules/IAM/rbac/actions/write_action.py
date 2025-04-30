from .action import Action
from ..enums import ActionTypes,Scopes

class WriteAction(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.WRITE)
        
    def is_permitted(self, scope):
        return self.scope[Scopes.PERMITTED] 
    
    def check_role_permission(self, scope):
        return self.scope[Scopes.PERMITTED] 
                
    def allow_write(self):
        self.scope[Scopes.PERMITTED] = True
    
    def disallow_write(self):
        self.scope[Scopes.PERMITTED] = False