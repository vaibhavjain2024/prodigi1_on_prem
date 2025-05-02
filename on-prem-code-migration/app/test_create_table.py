from sqlalchemy import create_engine
from shared.IAM.repositories.db_setup import Base

# Replace with your actual connection string
connection_string = "postgresql://postgres:platformpassword@platform-postgres:5432/platform-db"
engine = create_engine(connection_string)

# Create tables
Base.metadata.create_all(engine)
print("Tables created successfully!")