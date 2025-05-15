from .repository import Repository
from .models.msil_shift import MSILShift
from sqlalchemy.orm import Session
import datetime

class MSILShiftRepository(Repository):
    """MSILShiftRepository to manage MSILShift data table.
    
    Args:
        Repository (class): Base repository
    """
    def __init__(self, session: Session):
        self.session = session
        self.model_type = MSILShift

    def update_shifts(self, shifts, shop_id):
        with self.session:
            self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).delete()
            self.session.bulk_insert_mappings(mappings=shifts,mapper=self.model_type)
            self.session.commit()
    
    def get_shift(self,shop_id,time):
        with self.session:
            all_shifts = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).all()
            shift = None
            for each_shift in all_shifts:
                if each_shift.shift_start_timing <= time <= each_shift.shift_end_timing:
                    shift = each_shift.shift_name
            return shift
    
    def get_production_date(self,shift):
        if shift != "C":
            return datetime.datetime.today().strftime('%Y-%m-%d')
        return (datetime.datetime.today()  - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    def shift_end_times(self,shop_id):
        with self.session:
            all_shifts = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).all()
            end_times = []
            for each_shift in all_shifts:
                    et = each_shift.shift_end_timing
                    et = datetime.time(et.hour,et.minute)
                    end_times.append(et)
            return end_times

    def day_start_time(self,shop_id):
        with self.session:
            first_shift = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).order_by(self.model_type.shift_name).first()
            return first_shift.shift_start_timing
    
    def day_end_time(self,shop_id):
        with self.session:
            first_shift = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).order_by(self.model_type.shift_name.desc()).first()
            return first_shift.shift_end_timing
    
    def shift_name_start_end_list(self, shop_id):
        with self.session:
            shifts = self.session.query(self.model_type.shift_name,
                                        self.model_type.shift_start_timing, 
                                        self.model_type.shift_end_timing) \
                                .filter(self.model_type.shop_id==shop_id).all()
            return shifts
    
    def shift_object_list(self,shop_id):
        with self.session:
            shifts = self.session.query(self.model_type) \
                        .filter(self.model_type.shop_id == shop_id) \
                        .all()
            return shifts
        
    def get_shift_start_and_end_time(self,shop_id,time):
        with self.session:
            all_shifts = self.session.query(self.model_type).filter(self.model_type.shop_id==shop_id).all()
            shift = None
            for each_shift in all_shifts:
                if each_shift.shift_start_timing <= time <= each_shift.shift_end_timing:
                    shift = each_shift.shift_name
                    shift_start_timing = each_shift.shift_start_timing
                    shift_end_timing = each_shift.shift_end_timing
            return {"shift":shift,
                    "shift_start_timing": shift_start_timing,
                    "shift_end_timing":shift_end_timing}