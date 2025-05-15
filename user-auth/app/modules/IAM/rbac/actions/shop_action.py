from .action import Action
from ..enums import ActionTypes,Scopes, ReadLevels

class ShopAction(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.SHOP_ACTION)
        
    def is_permitted(self, scope):
        print("++++++++++++++++", scope[Scopes.ALLOWED_SHOP_IDS], self.scope[Scopes.ALLOWED_SHOP_IDS])
        if( self.scope[Scopes.ALLOWED_SHOP_IDS] == ["*"] \
            or scope[Scopes.ALLOWED_SHOP_IDS] in self.scope[Scopes.ALLOWED_SHOP_IDS] ) :
            return True
        return False

    def set_level(self, scope_level):
        self.set_scope[Scopes.ALLOWED_SHOP_IDS] = scope_level


                
