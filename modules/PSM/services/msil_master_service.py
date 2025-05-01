import datetime
from ..repositories.msil_master_repository import MSILDigiprodMasterRepository
from ..repositories.models.msil_digiprod_master import MSILDigiprodMaster, MasterFileStatusEnum
from .service import Service
import pytz 

ist_tz = pytz.timezone('Asia/Kolkata')

class MSILMasterService(Service):
    def __init__(self, repository : MSILDigiprodMasterRepository):
        self.repository = repository

    def check_if_new_master_can_be_uploaded(self, shop_id):
        ## Check if new master can be uploaded
        prev_master : MSILDigiprodMaster = self.repository.get_previous_file(shop_id=shop_id)
        if prev_master:
            if prev_master.file_status != MasterFileStatusEnum.REJECTED and \
               prev_master.file_status != MasterFileStatusEnum.APPROVED and \
               prev_master.file_status != MasterFileStatusEnum.UPLOAD_FAILED:
                return None
            return prev_master.version
        return 0
    
    def add_new_master(self, master_obj):
        shop_id = master_obj["shop_id"]
        master : MSILDigiprodMaster = self.repository.get_previous_file(shop_id=shop_id)
        new_master = MSILDigiprodMaster()

        if master == None:    
            new_master.version = 1
        else:
            new_master.version = master.version + 1
        
        new_master.file_status = MasterFileStatusEnum.UPLOAD_IN_PROGRESS
        current_time = datetime.datetime.now(ist_tz).replace(tzinfo=None)

        new_master.shop_id = shop_id
        new_master.master_file_path = master_obj["master_file_name"]
        new_master.uploader_user_id = master_obj["upload_user_id"]
        new_master.uploader_user_name = master_obj["upload_user_name"]
        new_master.uploader_email = master_obj["uploader_email"]
        new_master.upload_date_time = current_time
        new_master.module_name = master_obj["module_name"]
        new_master.shop_name = master_obj["shop_name"]
        new_master.plant_name = master_obj["plant_name"]
        new_master.site_name = master_obj["site_name"]
        new_master.site_location = master_obj["site_location"]
        new_master.reviewer_email = master_obj["reviewer_email"]
        new_master.reviewer_id = master_obj["reviewer_id"]
        new_master.reviewer_name = master_obj["reviewer_name"]
        new_master = self.repository.add(new_master)

        master_obj["version"] = new_master.version
        master_obj["upload_date_time"] = current_time
        return master_obj
    
    def update_master_status(self, shop_id,version,status,error=None,review_date=None,initiate_date=None):
        self.repository.update_master_status(shop_id=shop_id,version=version,status=status,error=error,review_date=review_date,initiate_date=initiate_date)

    def get_masters(self, shop_id):
        masters = self.repository.get_masters(shop_id)  
        master_list = []
        approved = False
        for master in masters:
            master_obj = {
                "id" : master.id,
                "uploader_user_id" : master.uploader_user_id,
                "uploader_user_name" : master.uploader_user_name,
                "uploader_email" : master.uploader_email,
                "upload_date_time" : master.upload_date_time,
                "reviewer_id" : master.reviewer_id,
                "reviewer_name" : master.reviewer_name,
                "reviewer_email" : master.reviewer_email,
                "review_initiated_date" : master.review_initiated_date,
                "review_date" : master.review_date,
                "master_file_path" : master.master_file_path,
                "module_name" : master.module_name,
                "shop_name" : master.shop_name,
                "plant_name" : master.plant_name,
                "site_location" : master.site_location, 
                "site_name" : master.site_name,
                "version" : master.version,
                "shop_id" : master.shop_id,
                "file_status" : master.file_status,
                "errorMessages": str(master.error_messages).split('; ')
            }    
            if master.file_status:
                master_obj["file_status"] =  master.file_status.name
            if not approved and master_obj["file_status"]==MasterFileStatusEnum.APPROVED.name:
                approved=True
                approved_obj = master_obj
            else:
                master_list.append(master_obj)
        if approved: 
            master_list.insert(0,approved_obj) 
        return master_list
    
    def get_master_shop_version(self,shop,version):
        master = self.repository.get_master_shop_version(shop=shop,version=version)
        if master:
            master_obj = {
                "id" : master.id,
                "uploader_user_id" : master.uploader_user_id,
                "uploader_user_name" : master.uploader_user_name,
                "uploader_email" : master.uploader_email,
                "upload_date_time" : master.upload_date_time,
                "reviewer_id" : master.reviewer_id,
                "reviewer_name" : master.reviewer_name,
                "reviewer_email" : master.reviewer_email,
                "review_initiated_date" : master.review_initiated_date,
                "review_date" : master.review_date,
                "master_file_path" : master.master_file_path,
                "module_name" : master.module_name,
                "shop_name" : master.shop_name,
                "plant_name" : master.plant_name,
                "site_location" : master.site_location, 
                "site_name" : master.site_name,
                "version" : master.version,
                "shop_id" : master.shop_id,
                "file_status" : master.file_status
            }
            # result = self.transform_model_to_dict(result)
            return master_obj
        return None

    