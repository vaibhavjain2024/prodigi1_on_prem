from sqlalchemy import or_, and_, literal, func

from .models.iot_module import IoTModule
from .models.iot_msil_site import MSILSite
from .models.iot_msil_location import MSILLocation
from .models.iot_msil_plant import MSILPlant
from .models.iot_msil_shop import MSILShop 
from .models.iot_module_shop_association_table import IOTModuleShopAssociation
from .models.iot_module_location_association import IOTModuleLocationAssociation
from .models.iot_smm_role_master import SMMRoleMaster
from .repository import Repository
from sqlalchemy.orm import joinedload


class ShopRepository(Repository):
    """Module repository to manage iot-module table

    Args:
        Repository (class): Base repository
    """

    def __init__(self, session):
        self.session = session
        self.model_type = MSILShop

    def get_all_values(self):
        with self.session:
            return (
                self.session.query(
                    IoTModule.module_name.label("module"),
                    MSILSite.site_name.label("site"),
                    MSILLocation.location_name.label("location"),
                    MSILPlant.plant_name.label("plant"),
                    self.model_type.shop_name.label("shop"),
                    IoTModule.display_name.label("module_display_name"),
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
                )
                .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .join(MSILLocation, MSILLocation.id == MSILPlant.location_id)
                .join(MSILSite, MSILSite.id == MSILLocation.site_id)
                .all()
            )
    
    def get_all_values_for_location_associations(self):
        with self.session:
            return (
                self.session.query(
                    # IoTModule.id.label("id"),
                    IoTModule.module_name.label("module"),
                    MSILSite.site_name.label("site"),
                    MSILLocation.location_name.label("location"),
                    MSILPlant.plant_name.label("plant"),
                    literal('').label("shop"),
                    IoTModule.display_name.label("module_display_name"),
                ).join(
                    IOTModuleLocationAssociation,
                    IoTModule.id == IOTModuleLocationAssociation.iot_module_id
                ).join(
                    MSILLocation,
                    IOTModuleLocationAssociation.iot_msil_location_id == MSILLocation.id
                ).join(
                    MSILSite,
                    MSILLocation.site_id == MSILSite.id
                ).join(
                    MSILPlant,
                    MSILPlant.location_id == MSILLocation.id
                ).all()
            )

    def get_all_values_by_filter_values(
        self, module_name, site_name, location_name, plant_name, shop_name
    ):
        with self.session:
            query = (
                self.session.query(
                    IoTModule.module_name,
                    MSILSite.site_name,
                    MSILLocation.location_name,
                    MSILPlant.plant_name,
                    self.model_type.shop_name,
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
                )
                .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .join(MSILLocation, MSILLocation.id == MSILPlant.location_id)
                .join(MSILSite, MSILSite.id == MSILLocation.site_id)
            )
            if module_name != "All":
                query = query.filter(IoTModule.module_name == module_name)
            if site_name != "All":
                query = query.filter(MSILSite.site_name == site_name)
            if location_name != "All":
                query = query.filter(MSILLocation.location_name == location_name)
            if plant_name != "All":
                query = query.filter(MSILPlant.plant_name == plant_name)
            if shop_name != "All":
                query = query.filter(MSILShop.shop_name == shop_name)
            return query.all()

    def get_shops_by_module(self, module_name):
        with self.session:
            query = (
                self.session.query(
                    self.model_type, IoTModule, MSILSite, MSILLocation, MSILPlant
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
                )
                .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
                .filter(IoTModule.module_name == module_name)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .join(MSILLocation, MSILLocation.id == MSILPlant.location_id)
                .join(MSILSite, MSILSite.id == MSILLocation.site_id)
            )
            return query.all()

    def get_shops_by_plant_id_or_type_repair(
        self, plant_id, repair: list = None
    ) -> list:
        with self.session:
            if repair:
                or_filters = [MSILPlant.id == plant_id]

                for repair_filter in repair:
                    or_filters.append(self.model_type.shop_type == repair_filter)

                filters = [or_(*or_filters)]

            else:
                filters = [MSILPlant.id == plant_id]

            query = (
                self.session.query(
                    self.model_type.id,
                    self.model_type.plant_id,
                    self.model_type.shop_name,
                    self.model_type.shop_type,
                    MSILPlant.plant_name,
                )
                .select_from(MSILPlant)
                .join(
                    self.model_type,
                    self.model_type.plant_id == MSILPlant.id,
                )
                .filter(*filters)
                .all()
            )

            return query

    def collect_shop_and_plant_ids(self, shop_ids):
        with self.session:
            # Query to retrieve shop names and their corresponding plant ids
            shop_plant_data = (
                self.session.query(
                    self.model_type.id,
                    self.model_type.shop_name,
                    self.model_type.plant_id,
                    MSILPlant.plant_name,
                )
                .select_from(self.model_type)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .filter(self.model_type.id.in_(shop_ids))
                .all()
            )

        return shop_plant_data

    def get_plant_and_common_shops(self, shop_id ):
        with self.session:
            # Query to get the plant ID and plant name based on the provided shop ID
            plant_query = (
                self.session.query(self.model_type.plant_id, MSILPlant.plant_name)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .filter(self.model_type.id == shop_id)
                .first()
            )

            if not plant_query:
                # Shop ID not found, return an empty result
                return {}

            plant_id, plant_name = plant_query
            common_shop_types = ["Bumper", "Engine", "TRANSMISSION"]

            # Query to retrieve all shops in the same plant
            related_shops_query = (
                self.session.query(self.model_type.id, self.model_type.shop_name)
                .select_from(self.model_type)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .filter(
                    or_(
                        self.model_type.shop_type.in_(common_shop_types),
                        self.model_type.plant_id == plant_id,
                    )
                )
                .filter(
                    self.model_type.shop_name != "NOT_IN_USE" 
                )
                .filter(
                    self.model_type.shop_type != "Vehicle Inspection" 
                )
                .all()
            )
            shop_names = list(map(lambda x: x[1], related_shops_query))
            return related_shops_query, shop_names

    def get_shop_name(self, shop_id):
        with self.session:
            shop_name = (
                self.session.query(
                    self.model_type.shop_name,
                )
                .select_from(self.model_type)
                .filter(self.model_type.id == shop_id)
                .first()[0]
            )
            return shop_name

    def get_shop_group_line_area_details(self, module_name):
        query = (
            self.session.query(
                self.model_type,
                IoTModule,
                MSILSite,
                MSILLocation,
                MSILPlant,
                SMMRoleMaster
            )
            .join(
                IOTModuleShopAssociation,
                IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
            )
            .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
            .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
            .join(MSILLocation, MSILLocation.id == MSILPlant.location_id)
            .join(MSILSite, MSILSite.id == MSILLocation.site_id)
            .join(SMMRoleMaster, self.model_type.id == SMMRoleMaster.shop_id)
            .filter(IoTModule.module_name == module_name)
        )
        return query.all()

    def check_if_args_exist_in_role_master(
            self, staff_id, group_name=None, line_name=None, area_name=None
    ):
        with self.session:
            query = self.session.query(SMMRoleMaster)

            filters = [
                or_(
                    SMMRoleMaster.area_supervisor_id == staff_id,
                    SMMRoleMaster.line_incharge_id == staff_id,
                    SMMRoleMaster.group_shift_incharge == staff_id,
                    SMMRoleMaster.shop_quality_incharge == staff_id,
                ),
                SMMRoleMaster.is_active == True
            ]

            if filters:
                query = query.filter(and_(*filters))

            result = query.first()
            list_ = []
            if result:
                entry = {
                    "plant_id": result.plant_id,
                    "plant_name": result.plant_name,
                    "shop_id": result.shop_id,
                    "shop_name": result.shop_name,
                    "subcategory": result.sub_category
                }
                if staff_id == result.line_incharge_id:
                    entry.update({
                        "group": result.group_name,
                        "line": result.line_name
                    })
                elif staff_id == result.group_shift_incharge:
                    entry.update({
                        "group": result.group_name
                    })
                elif staff_id == result.area_supervisor_id:
                    entry.update({
                        "group": result.group_name,
                        "line": result.line_name,
                        "area": result.area_name
                    })
                list_.append(entry)
                return list_
            else:
                return {}

    def get_shops_by_module_id(self, module_id):
        with self.session:
            query = (
                self.session.query(
                    self.model_type, IoTModule, MSILSite, MSILLocation, MSILPlant
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
                )
                .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
                .filter(IoTModule.id == module_id)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .join(MSILLocation, MSILLocation.id == MSILPlant.location_id)
                .join(MSILSite, MSILSite.id == MSILLocation.site_id)
            )
            return query.all()
    
    def get_location_id_by_location_name(self,location_name):
        with self.session:
            return self.session.query(MSILLocation.id) \
                    .filter(MSILLocation.location_name == location_name) \
                    .first()
            


    def get_module_shop_association(self):

        with self.session:
            query = (
                self.session.query(
                    self.model_type.id, self.model_type.shop_name, IoTModule.id, IoTModule.module_name
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_module_id == IoTModule.id,
                )
                .join(self.model_type, IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id)
            )

            return query.all()
        
    def get_modules_names_and_id(self):
        with self.session:
            return self.session.query(IoTModule).all()

    def get_shop_type(self, shop_id):
        with self.session:
            shop_type = (
                self.session.query(
                    self.model_type.shop_type
                )
                .select_from(self.model_type)
                .filter(self.model_type.id == shop_id)
                .first()[0]
            )
            return shop_type

    
    def get_shop_detail_by_module_ids(self, module_ids):
        with self.session:
            query = (
                self.session.query(
                    IoTModule.id,
                    IoTModule.module_name,
                    IoTModule.display_name,
                    IOTModuleShopAssociation.iot_msil_shop_id,
                    self.model_type.shop_name,
                    self.model_type.shop_type
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
                )
                .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
                .filter(IoTModule.id.in_(module_ids))
            )
            return query.all()
        
    def get_all_module(self, limit= 1000, offset= 0):
        with self.session: 
            return self.session.query(IoTModule).limit(limit).offset(offset).all()
        
    def get_location_details_by_module_ids(self, module_ids):
        with self.session as session:
            query = ( 
                session.query(
                    IoTModule.id,
                    IoTModule.module_name,
                    IoTModule.display_name,
                    IOTModuleLocationAssociation.iot_msil_location_id,
                    MSILLocation.location_name,
                )
                .join(
                    IOTModuleLocationAssociation,
                    IOTModuleLocationAssociation.iot_msil_location_id == MSILLocation.id,
                )
                .join(IoTModule, IOTModuleLocationAssociation.iot_module_id == IoTModule.id)
                .filter(IoTModule.id.in_(module_ids))
            )
            return query.all()

    def get_shops(self, module='Process Quality and Capability'):
        shop_list = self.session.query(
            IOTModuleShopAssociation
        ).join(
            IoTModule
        ).join(
            MSILShop
        ).filter(IoTModule.module_name == module).distinct(MSILShop.id).with_entities(MSILShop.shop_name, MSILShop.id)
        return shop_list
    
        

    def get_shop_id(self, shop_name):
        with self.session:
            shop_id = (
                self.session.query(
                    self.model_type.id,
                )
                .select_from(self.model_type)
                .filter(self.model_type.shop_name == shop_name)
                .first()[0]
            )
            return shop_id

    def get_all_plants(self):
        with self.session: 
            return self.session.query(MSILPlant).all()
        
    def get_all_shops_by_shop_type(self, shop_type):
        with self.session: 
            return self.session.query(MSILShop).filter(MSILShop.shop_type.ilike(shop_type)).all()
        
    def get_locations_by_module(self, module_ids):
        with self.session:
            query = (
                self.session.query(
                    IoTModule.id.label("module_id"),
                    IoTModule.module_name.label("module_name"),
                    self.model_type.id.label('shop_id'),
                    MSILPlant.id.label('plant_id'),
                    MSILLocation.id.label('location_id'),
                    MSILLocation.location_name.label('location_name'),
                    IoTModule.display_name.label("module_display_name"),
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
                )
                .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
                .filter(IoTModule.id.in_(module_ids))
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .join(MSILLocation, MSILLocation.id == MSILPlant.location_id)
            )
            return query.all()
    
    def get_all_locations(self):
        with self.session: 
            return self.session.query(MSILLocation).all()
    
    def get_location_wise_shops_by_module(self, module_name):
        with self.session as session:
            query = (
                session.query(
                    MSILLocation.location_name.label("location"),
                    func.array_agg(self.model_type.shop_name).label("shop_names")
                )
                .join(
                    IOTModuleShopAssociation,
                    IOTModuleShopAssociation.iot_msil_shop_id == self.model_type.id,
                )
                .join(IoTModule, IOTModuleShopAssociation.iot_module_id == IoTModule.id)
                .filter(IoTModule.module_name == module_name)
                .join(MSILPlant, MSILPlant.id == self.model_type.plant_id)
                .join(MSILLocation, MSILLocation.id == MSILPlant.location_id)
                .group_by(MSILLocation.location_name)
            )
            # Execute the query
            results = session.execute(query).all()
            # Format results for output
            formatted_results = [
                {"location": row.location, "shop_names": row.shop_names}
                for row in results
            ]
            return formatted_results
    
    def get_all_sites(self):
        with self.session: 
            return self.session.query(MSILSite).all()