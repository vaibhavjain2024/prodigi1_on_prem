from .models.user import User
from .models.permission import Permission
from .models.role import Role
from .models.user_role import UserRole
from .repository import Repository
from sqlalchemy import desc, or_, text


class UserRepository(Repository):
    """Role reportory to manage role table

    Args:
        Repository (class): Base repository
    """    
    def __init__(self, session):
        self.session = session
        self.model_type = User

    def get_users(self, tenant):
        """Get all users for a tenant
        """
        with self.session as session:         
            return session.query(self.model_type).filter_by(tenant=tenant).all()
        # return self.session.query(self.model_type).filter_by(tenant=tenant).all()

    def get_adfs_users(self, page_number, page_size):
        """Get all users for a tenant
        """
        with self.session as session:
            query = session.query(self.model_type).filter_by(tenant='ADFS')
            query = query.offset((page_number - 1) * page_size) \
                .limit(page_size).all()
            return query

    def get_user_by_federation_identifier(self,identifier):
        with self.session as session: 
            return session.query(self.model_type).filter_by(federation_identifier=identifier).first()
        # return self.session.query(self.model_type).filter_by(federation_identifier=identifier).first()

    def get_all_users(self,page_number,page_size):
        """Get all users
        """
        with self.session as session:         
            query =  session.query(self.model_type).order_by(desc(self.model_type.id))
            query = query.offset((page_number-1)*page_size) \
                    .limit(page_size).all()
            return query
        # return self.session.query(self.model_type).filter_by(tenant=tenant).all()

    def get_emails_by_user_ids(self,user_ids):
        with self.session as session:         
            query =  session.query(self.model_type.email_id,
                                    self.model_type.id).filter(self.model_type.id.in_(user_ids)).all()
            return query

    def search_user_info(self, query_str):
        with self.session as session:
            users = (
                session.query(self.model_type)
                .filter(
                    or_(
                        self.model_type.federation_identifier.ilike(f"%{query_str}%"),
                        self.model_type.email_id.ilike(f"%{query_str}%"),
                    ),
                    self.model_type.email_id.isnot(None),
                    self.model_type.federation_identifier.isnot(None)
                )
                .all()
            )
            return users

    def get_unique_roles_by_shop_ids(
            self,
            shop_ids
        ):
        with self.session: 
            # Construct the raw SQL query using `text`
            query = text(f"""
                SELECT DISTINCT role_id 
                FROM "iot-permission" ip 
                WHERE EXISTS (
                    SELECT 1 
                    FROM pg_catalog.jsonb_array_elements_text(scope->'ALLOWED_SHOP_IDS') AS shop_id
                    WHERE shop_id::text = ANY(:shop_ids_array)
                )
            """)
            result = self.session.execute(query, {'shop_ids_array': shop_ids}).fetchall()
            unique_role_ids = [row[0] for row in result]
            return unique_role_ids
    
    def get_unique_roles_by_location_ids(
            self,
            location_ids
        ):
        with self.session: 
            # Construct the raw SQL query using `text`
            query = text(f"""
                SELECT DISTINCT role_id 
                FROM "iot-permission" ip 
                WHERE (
                    EXISTS (
                        SELECT 1 
                        FROM pg_catalog.jsonb_array_elements_text(scope->'ALLOWED_SHOP_IDS') AS shop_id
                        WHERE shop_id::text = ANY(:shop_ids_array)
                    )
                    OR EXISTS (
                        SELECT 1 
                        FROM pg_catalog.jsonb_array_elements_text(scope->'ALLOWED_LOCATION_IDS') AS location_id
                        WHERE location_id::text = ANY(:shop_ids_array)
                    ) 
                )
                AND (scope->>'IS_ASSOCIATED_TO_LOCATION')::text = 'true'
            """)
            result = self.session.execute(query, {'shop_ids_array': location_ids}).fetchall()
            unique_role_ids = [row[0] for row in result]
            return unique_role_ids
    
    def search_user_with_advance_params(
            self,
            usernames,
            user_types,
            resource_names,
            role_ids,
            page_number,
            page_size,
            shop_ids,
            location_ids = [],
            skip_pagination = False
        ):
        with self.session:
            query = self.session.query(
                self.model_type,
                Role,
                Permission
            )
            if len(usernames):
                query = query.filter(self.model_type.federation_identifier.in_(usernames))
            
            if len(user_types):
                query = query.filter(self.model_type.tenant.in_(user_types))
            
            query = query.distinct(
                self.model_type.id
            ).join(
                UserRole,
                UserRole.user_id == self.model_type.id
            ).join(
                Role,
                Role.id == UserRole.role_id
            ).join(
                Permission,
                Permission.role_id == Role.id
            )

            passive_filter_on_role_id = False

            if len(shop_ids):
                role_ids_via_shop = self.get_unique_roles_by_shop_ids(shop_ids)
                role_ids_via_shop += role_ids
                role_ids = list(set(role_ids_via_shop))
                passive_filter_on_role_id = True
            
            if len(location_ids):
                role_ids_via_location = self.get_unique_roles_by_location_ids(location_ids)
                role_ids_via_location += role_ids
                role_ids = list(set(role_ids_via_location))
                passive_filter_on_role_id = True

            if len(resource_names):
                query = query.filter(Permission.resource.in_(resource_names))
            if passive_filter_on_role_id == True or len(role_ids):
                query = query.filter(Permission.role_id.in_(role_ids))
            
            # Apply sorting
            query = query.order_by( self.model_type.id.desc())
            
            # Apply Pagination
            if skip_pagination == False:
                limit = page_size
                offset = (page_number-1)*page_size
                query = query.limit(limit).offset(offset)
            
            return query.all()
