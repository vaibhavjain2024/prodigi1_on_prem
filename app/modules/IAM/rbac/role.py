from .permission import Permission
from .enums import *
class Role(object):
    """Role class containing data and functionality for a role
    
    """    
    def __init__(self, role_name, is_superadmin=False, is_admin=False):
        self.role_name = role_name
        self.is_admin = is_admin
        self.is_superadmin = is_superadmin
    
    def add_permission_actions(self,resource_name,action,permission_object,user_permissions):
        if self.permissions.__contains__(resource_name) :
            if self.permissions[resource_name].get_actions().__contains__(action["name"]):
                stored_action = self.permissions[resource_name].get_actions()[action["name"]]
                stored_scopes = stored_action.get_scopes()
                scope_update={}
                for scope in action["scope"]:
                    if(stored_scopes.__contains__(scope)):
                        if(user_permissions):
                                scope_update[scope]= action['scope'][scope]
                        else :
                            if(isinstance(stored_scopes[scope],int)):
                                scope_update[scope]= min([stored_action.get_scopes()[scope],action['scope'][scope]]) 

                            if(isinstance(stored_scopes[scope],list)):
                                scope_update[scope] = list(set(stored_action.get_scopes()[scope]) | set(action['scope'][scope]))
                            if(isinstance(stored_scopes[scope],bool)):
                                scope_update[scope]= stored_action.get_scopes()[scope] or action['scope'][scope]

                stored_action.set_scope(scope_update)
            else:
                permission_object.add_action(action=action)
        else:
            permission_object.add_action(action=action)


        
    def get_permission_object(self,resource_name):
        if self.permissions.__contains__(resource_name) :
            return self.permissions[resource_name]
        else :
            return Permission(resource=resource_name)
        
    def add_permissions_to_role(self,role_dict,user_permissions):
        # print(role_dict)
        resource_name = role_dict["resource"]
        action ={"name":role_dict["action"],"scope":role_dict["scope"],"type":role_dict["action_type"]}
        permission_object = self.get_permission_object(resource_name)
        self.add_permission_actions(resource_name,action,permission_object,user_permissions)
        self.permissions[resource_name] = permission_object
        # for permission in role_dict["permissions"]:
        #     for permission_dict in permission:
        #         for permission_details in permission_dict :
        #             print(permission_dict[permission_details])
                
        #             resource_name = permission_dict[permission_details]["resource"]
        #             permission_object = self.get_permission_object(resource_name)
        #             for action in permission_dict[permission_details]["actions"]:
        #                 self.add_permission_actions(resource_name,action,permission_object,user_permissions)
        #             self.permissions[resource_name] = permission_object
        
    def parse_role(self,role_dicts,user_permissions=None):
        self.permissions = {}
        for role_dict in role_dicts:
            self.add_permissions_to_role(role_dict,False)
        if(user_permissions!=None ):
            self.add_permissions_to_role(user_permissions,True)
                  
    def check_permission(self,resource_name, action, scope=""):
        #Check if role has any permission for the resource 
        if self.permissions.__contains__(resource_name) is False:
            return False
        
        try:
            permission = self.permissions[resource_name]
            #Check if role has any permission for the action 
            return permission.check_permission(action_name=action,scope=scope)
        except :
            return False

    def check_role_assign_permission(self,role_dict):
        if(self.is_superadmin ):
            return True
        if(self.is_admin):
            return True
        permissions = role_dict["permissions"]
        print(permissions)
        for permission in permissions:
            resource_name = permissions[permission]["resource"]
            if self.permissions.__contains__(resource_name) is False:
                return False
            self_permission = self.permissions[resource_name]
            for action in permissions[permission]["actions"]:
                if(self_permission.check_role_permission(action_name = action["name"],scope =action["scope"]) is False):
                    return False
        return True
        
            

        
    def check_superadmin(self):
        return self.is_superadmin

    def check_admin(self):
        return self.is_admin