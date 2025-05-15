import uuid
from sqlalchemy.sql.expression import except_
from ..repositories.user_repository import UserRepository
from ..repositories.role_repository import RoleRepository
from .role_service import RoleService
from ..repositories.user_role_repository import UserRoleRepository
from ..repositories.models.user_role import UserRole
from ..repositories.models.user import User
from ..repositories.models.role import Role


class UserService():
    def __init__(self, repository : UserRepository):
        self.repository = repository
        self.role_repository = RoleRepository(self.repository.session)
        self.role_service = RoleService(self.role_repository)
        self.user_role_repository = UserRoleRepository(self.repository.session)

    
    def get_user(self,user_id):
        user_id = (user_id)
        user_model = self.repository.get(user_id)
        if(user_model!=None):
            return self.transform_from_model(user_model)
        else:
            return None
    
    def get_user_by_federation_identifier(self,identifier):
        user_model = self.repository.get_user_by_federation_identifier(identifier)
        if(user_model!=None):
            return self.transform_from_model(user_model)
        else:
            return None


    def create_user(self, user):
        user_model = User()
        self.transform_from_dict(user_model, user)
        self.repository.add(user_model)
        user["id"] = str(user_model.id)
        for role in user.get("roles",[]):
            user_role = UserRole()
            user_role.user_id = user["id"]
            role_details = self.role_service.get_role_by_name_and_tenant_name(role, user["tenant"])
            if(role_details!=None):
                user_role.role_id = role_details["id"]
                self.user_role_repository.add(user_role)
        return user

    def get_roles_list(self,user_roles):
        roles= []
        for user_role in user_roles:
            roles.append(user_role.role_id)
        
        return roles

    def update_user_lastlogged_in(self,user):
        user_model = self.repository.get_user_by_federation_identifier(user["federation_identifier"])
        print(user_model.last_loggedin)
        print(user["last_loggedin"])
        #user_model["last_loggedin"] = user["last_loggedin"]
        user["id"] = user_model.id
        user["tenant"] = user_model.tenant
        self.repository.update(user_model.id,user)

    def update_user(self,user):
        user_model = self.repository.get_user_by_federation_identifier(user["federation_identifier"])
        if(user_model!=None):
            update_user_dict = user
            updated_roles = []
            if(update_user_dict.get("roles" , None) != None):
                updated_roles = update_user_dict["roles"]
                del update_user_dict["roles"]
            self.repository.update(user_model.id,update_user_dict)
            user_roles = self.user_role_repository.get_user_role_by_user_id(user_model.id)
            #roles_list = self.get_roles_list(user_roles)
            for prev_role in user_roles:
                self.user_role_repository.remove_role(prev_role)
            for role in updated_roles:
                user_role = UserRole()
                user_role.user_id = user_model.id
                role_details = self.role_service.get_role_by_name_and_tenant_name(role,user["tenant"])
                if(role_details!=None):
                    user_role.role_id = role_details["id"]
                    self.user_role_repository.add(user_role)

            return user
        else:
            return None

    def get_roles(self,user_roles):
        roles = []
        for user_role in user_roles:
            roles.append(self.role_service.get_role(user_role.role_id))
        return roles

    def transform_from_model(self, model):
        role_details = self.get_roles(model.roles)
        return{
            "federation_identifier" : model.federation_identifier,
            "roles" :[ role["name"] for role in  role_details],
            "role_permissions":self.get_role_permissions(role_details),
            "is_admin" : self.check_user_is_admin(role_details),
            "is_super_admin" : self.check_user_is_super_admin(role_details),
            "tenant":model.tenant,
            "last_loggedin":model.last_loggedin
        }

    def transform_from_dict(self, model, model_dict):
        if model_dict.get("federation_identifier", None) != None:
            model.federation_identifier = model_dict["federation_identifier"]
        if model_dict.get("tenant", None) != None:
            model.tenant = model_dict["tenant"]
        if model_dict.get("last_loggedin", None) != None:
            model.last_loggedin = model_dict["last_loggedin"]

    def get_role_permissions(self,role_details):
        permission_list = []
        try:
            for role in role_details:
                for permission in role["permissions"]:
                    permission_list.append(permission)
            return permission_list
        except:
            return []

    def check_user_is_admin(self,role_details):
        try:
            is_admin = False
            for role in role_details:
                if(role.get("is_admin",None) == True):
                    is_admin = True
                    return is_admin
        except:
            return False
    
    def check_user_is_super_admin(self,role_details):
        try:
            is_super_admin = False
            for role in role_details:
                if(role.get("is_super_admin",None) == True):
                    is_super_admin = True
                    return is_super_admin
        except:
            return False

    def create_user_with_roles(self, user_data: dict):
        user_id = user_data.get("id")
        federation_identifier = user_data.get("federation_identifier")
        tenant = user_data.get("role", {}).get("tenant")
        email_id = user_data.get("email_id")
        username = user_data.get("username")

        user = self.repository.get(user_id)
        if not user:
            user = User(
                id=user_id,
                federation_identifier=federation_identifier,
                tenant=tenant,
                email_id=email_id,
                user_name=username
            )
            self.repository.add(user)

        # Roles and permissions
        permissions_obj = user_data.get("role", {}).get("permissions", [{}])
        if permissions_obj:
            role_id = permissions_obj[0].get("role_id")
            is_admin = user_data.get("role", {}).get("is_admin", False)
            is_super_admin = user_data.get("role", {}).get("is_super_admin", False)

            role = self.role_repository.get(role_id)
            if not role:
                role = Role(
                    id=role_id,
                    tenant=tenant,
                    is_admin=is_admin,
                    is_super_admin=is_super_admin
                )
                self.role_repository.add(role)

            # User-Role mapping
            user_role = self.user_role_repository.get_by_user_and_role(user_id, role_id)
            if not user_role:
                user_role = UserRole(
                    user_id=user_id,
                    role_id=role_id,
                    role=role
                )
                self.user_role_repository.add(user_role)

        return user