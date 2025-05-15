# user_table_name = os.getenv("MONGO_PROCHECK_USERS_TABLE_NAME", "procheck-users")
from app.config.app_config import MONGO_PROCHECK_USERS_TABLE_NAME as user_table_name
from app.db import database

user_collection = database.get_collection(user_table_name)
user_collection.create_index([("username", 1), ("email", 1)], unique=True)


async def get_user_record_from_mongo(record):
    try:
        result = await user_collection.find_one(record)
        return result
    except Exception as e:
        print('repos', e)


async def insert_user_record_in_mongo(record):
   return await user_collection.insert_one(record)


async def insert_user_records_in_mongo(record):
   return await user_collection.insert_many(record)


async def update_user_record_in_mongo(filter_data, user_record):
    result = await user_collection.update_one(filter_data,
                        {"$set": user_record, "$unset": {"permissions": "", "id":""} },
                    )
    return result


async def delete_user_record_from_mongo(record):
    result = await user_collection.delete_one(record)
    return result


