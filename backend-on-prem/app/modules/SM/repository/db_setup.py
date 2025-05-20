from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

def get_session(session, engine):
    from .models.iot_module import IoTModule
    from .models.iot_msil_site import MSILSite
    from .models.iot_msil_location import MSILLocation
    from .models.iot_msil_plant import MSILPlant
    from .models.iot_msil_shop import MSILShop
    from .models.iot_module_shop_association_table import IOTModuleShopAssociation
    from .models.iot_smm_role_master import SMMRoleMaster
    
    Base.metadata.create_all(engine)
    return session










