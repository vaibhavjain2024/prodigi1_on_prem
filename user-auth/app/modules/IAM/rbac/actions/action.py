class Action(object):
    def __init__(self, action_type):
        self.action_type = action_type

    def set_scope(self, scope):
        self.scope = scope

    def get_scope(self, scope):
        return self.scope

    def get_scopes(self):
        return self.scope
    
    def is_permitted(self, scope):
        #to be implemented by child classes
        raise NotImplementedError("Child class must override is_permitted method")

    def check_role_permission(self, scope):
        #to be implemented by child classes
        raise NotImplementedError("Child class must override can assign role method")



