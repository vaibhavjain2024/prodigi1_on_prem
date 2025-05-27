from .rbac.role import Role
from .repositories.role_repository import RoleRepository
from .services.role_service import RoleService
from .services.user_service import UserService
from .repositories.user_repository import UserRepository


def get_role(identifier, session):
    role_repository = RoleRepository(session)
    role_service = RoleService(role_repository)

    user_repository = UserRepository(session)
    user_service = UserService(user_repository)
    # user = user_service.get_user_by_federation_identifier(identifier)
    user = user_service.get_user_by_federation_identifier(identifier) or user_service.get_user_by_federation_identifier("maruti\\" + identifier) or user_service.get_user_by_federation_identifier("msil-iot_maruti\\" + identifier)
    role = Role("role", user["is_super_admin"], user["is_admin"])
    role.parse_role(user["role_permissions"])
    print(role.permissions)
    return role

def get_role_by_role_name_and_tenant_name(role_name,tenant_name, session):
    role_repository = RoleRepository(session)
    role_service = RoleService(role_repository)

    user_repository = UserRepository(session)
    user_service = UserService(user_repository)
    role_permissions = role_service.get_role_by_name_and_tenant_name(role_name,tenant_name)
    print("#############",role_permissions)
    role = Role("role",False,False)
    role.parse_role([{"permissions":role_permissions["permissions"]}])
    print(role.permissions)
    return role
