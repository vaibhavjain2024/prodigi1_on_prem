from .action import Action
from ..enums import ActionTypes,Scopes, ReadLevels,ActuationLevels

class ActuateAction(Action):
    def __init__(self, scope):
        self.set_scope(scope)
        super().__init__(ActionTypes.ACTUATE)
        
    def is_permitted(self, scope):     
        if self.scope[Scopes.LEVEL]:
            
            if self.scope[Scopes.LEVEL] == ActuationLevels.ALL:
                return True
            
            if self.scope[Scopes.LEVEL] == ActuationLevels.AREA and self.check_if_list_is_a_subset(scope[Scopes.AREA],self.scope[Scopes.AREA]):
                return True
            
            if self.scope[Scopes.LEVEL] == ActuationLevels.ZONE and self.check_if_list_is_a_subset(scope[Scopes.ZONE],self.scope[Scopes.ZONE]):
                return True
                
            if self.scope[Scopes.HYBRID] == ActuationLevels.HYBRID and self.check_if_list_is_a_subset(
                scope[Scopes.AREA] + scope[Scopes.ZONE],
                self.scope[Scopes.AREA] + self.scope[Scopes.ZONE]):
                return True
                
        return False        
        
    def check_if_list_is_a_subset(self, subset_list, superset_list):
        return set(subset_list).issubset(set(superset_list))
            

    def set_level(self, scope_level):
        self.set_scope[Scopes.LEVEL] = scope_level