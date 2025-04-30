from .action import Action
from ..enums import ActionTypes,Scopes, ReadLevels

class LISTACTION(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.LIST)
        
    def is_permitted(self, scope):
        if( self.scope[Scopes.ALLOWED_SHOP_IDS] == ["*"] \
            or scope[Scopes.ALLOWED_SHOP_IDS] in self.scope[Scopes.ALLOWED_SHOP_IDS] ) :
            return True
        return False

    def set_level(self, scope_level):
        self.set_scope[Scopes.ALLOWED_SHOP_IDS] = scope_level


                

