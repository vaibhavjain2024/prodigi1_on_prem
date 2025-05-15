from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


#connection_string = os.environ.get("CONNECTION_STRING")
#engine = create_engine(connection_string, echo=True)
#engine =  create_engine("postgresql://postgres:msiliotplatform@msil-iot-platform-db.cpla9liyn1nn.ap-south-1.rds.amazonaws.com/msil-iot-platform-db", echo=True)

Base = declarative_base()

#Session = sessionmaker(bind=engine)

#session = Session()

#import domain models
# from .models.permission import Permission
# from .models.role import Role
# from .models.user import User
# from .models.user_role import UserRole

#Base.metadata.create_all(engine)

#create a new db session 
def get_session(session, engine):

    from .models.permission import Permission
    from .models.role import Role
    from .models.user import User
    from .models.user_role import UserRole
    Base.metadata.create_all(engine)
    return session




