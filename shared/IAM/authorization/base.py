#from mongoengine import connect


def authorize(authorizer):
    """Authorize decorator for authorizing functions for access control

    Args:
        authorizer (function): A function which is called with the arguments of 
                               the decorated functions. The authorization logic is 
                               provided by this function
    """    
    def auth_decorator(decorated_function):
        """The actual decorator which returns the wrapped function with cpmbined
        authorization logic and decorated_function logic
        Args:
            decorated_function ([function]): The decorated function
        """ 
        # @wrap(decorated_function)       
        def wrapper(*args,**kwargs):
            """wrapper functions includes decorator logic and have access to decorated_function
               It is passed the arguments of the decorated functions

            Returns:
                [kwargs]: Keyword arguments, passed to the decorated functions
            """            
            kwargs = authorizer(**kwargs)

            result = decorated_function(*args,**kwargs)
     
            return result
        return wrapper
    return auth_decorator




# def get_role(identifier):
#     user = user_service.get_user_by_federation_identifier(identifier)
#     role = Role("role",False,False)
#     role.parse_role(user["role_permissions"],user["permissions"])
#     return role

# try :
#     role = get_role("test2@gmail.com")
#     get_venue_list(role = role)
# except:
#     print("unauthorized access")

