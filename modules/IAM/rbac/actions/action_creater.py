from .shop_action import ShopAction
from .read_action import ReadAction
from .write_action import WriteAction
from .update_action import UpdateAction
from .actuate_action import ActuateAction
from .provision_action import ProvisionAction
from .delete_action import  DeleteAction
from .list_action import  LISTACTION
from .update_signature_action import  UpdateSignatureAction
from .download_action import DownloadAction
from .admin_action import AdminAction
from ..enums import ActionTypes

def get_action_object(action):
    """Returns action object from action dictionary
    Args:
        action (dict): contains keys name, type, scope
        action["name"] : string, name of the action
        action["type"] : string, type of the action (READ/WRITE/USECASE)
        action["scope"] : dict, containing scopes of action depending upon its type
    """    
    action_name = action["name"]
    action_type = action["type"]
    action_scope = action["scope"]
    
    if action_type == ActionTypes.READ:
        return ReadAction(action_scope)

    if action_type == ActionTypes.WRITE:
        return WriteAction(action_scope)


    if action_type == ActionTypes.UPDATE:
        return UpdateAction(action_scope)
    
    
    if action_type == ActionTypes.DELETE:
        return DeleteAction(action_scope)

    if action_type == ActionTypes.ACTUATE:
        return ActuateAction(action_scope)
    
    if action_type == ActionTypes.PROVISION:
        return ProvisionAction(action_scope)
    
    if action_type == ActionTypes.LIST:
        return LISTACTION(action_scope)
    
    if action_type == ActionTypes.UPDATE_SIGNATURE:
        return UpdateSignatureAction(action_scope)

    if action_type == ActionTypes.DOWNLOAD:
        return DownloadAction(action_scope)

    if action_type == ActionTypes.ADMIN:
        return AdminAction(action_scope)
    
    if action_type == ActionTypes.SHOP_ACTION:
        return ShopAction(action_scope)
    
    
    # if action_type == ActionTypes.CONNECT:
    #     return ConnectAction(action_scope)


    # raise Exception("Invalid or unknown action type")

def get_action_dict(action_name, action_type, scope):
    return {
        "name" : action_name,
        "type" : action_type,
        "scope" : scope
    }    