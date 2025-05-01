from .actions.action_creater import get_action_object

class Permission(object):
    """Permission class, containing data
     about the permissions granted for a resource
    """    
    def __init__(self,resource):
        """constructor

        Args:
            resource (string): Name of the resource for which this permission is granted
        """        
        self.resource = resource
        self.actions = {}
        
    def add_action(self, action):
        self.actions[action["name"]] = get_action_object(action=action)

    def get_actions(self):
        return self.actions
    
    def check_permission(self, action_name, scope):
        print("-----------", self.actions[action_name])
        return self.actions[action_name].is_permitted(scope=scope)
    
    def check_role_permission(self, action_name, scope):
        if(self.actions.__contains__(action_name) is False):
            return False
        return self.actions[action_name].check_role_permission(scope = scope)

